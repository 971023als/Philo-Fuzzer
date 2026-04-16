from typing import List, Dict, Any, Tuple
from harness.schemas.models import (
    AgentOutputSchema,
    AgentFinding,
    ConflictingJudgment,
    RiskContext,
)
from harness.scoring.risk_calculator import RiskCalculator

class ArbiterMergeEngine:
    """모든 철학자 에이전트의 결과를 병합하고 조율하는 총괄 엔진"""

    def __init__(self):
        self.risk_calculator = RiskCalculator()

    def merge_results(
        self,
        agent_outputs: List[AgentOutputSchema],
        context: RiskContext,
    ) -> Tuple[List[AgentFinding], List[ConflictingJudgment], List[str]]:
        """
        1. 모든 Finding을 수집
        2. 중복/유사 그룹핑 (Evidence ID/Finding Group 기준)
        3. 정책 룰 엔진(가드레일 및 스코어) 적용
        4. 종합된 공통 이슈 및 명확한 상충 판단(Conflict) 구조화
        """
        all_findings: List[Tuple[str, AgentFinding]] = []
        for output in agent_outputs:
            for finding in output.findings:
                # 득점 전 가드레일 적용 (derived claim 오염 방지 등)
                processed = self.risk_calculator.apply_evidence_guardrails(finding)
                all_findings.append((output.agent_name, processed))

        common_findings, conflicting_judgments = self._group_and_evaluate(all_findings, context)
        
        # 위험도 높은 순으로 정렬
        risk_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        common_findings.sort(key=lambda x: risk_order.get(x.risk_level, 99))

        # Top Risks 산출
        top_risks = [
            f.finding_title
            for f in common_findings
            if f.risk_level in ["CRITICAL", "HIGH"]
        ]
        
        return common_findings, conflicting_judgments, top_risks

    def _group_and_evaluate(
        self,
        all_findings: List[Tuple[str, AgentFinding]],
        context: RiskContext,
    ) -> Tuple[List[AgentFinding], List[ConflictingJudgment]]:
        """
        증거 기반의 클러스터링을 통해 에이전트별 의견을 통합하고,
        이견이 존재하는 경우 Arbiter의 Policy에 따라 이를 ConflictingJudgment 로 분리.
        새로운 증거를 절대 생성하지 않으며 기존 파인딩을 재조합함.
        """
        evidence_dict: Dict[str, List[Tuple[str, AgentFinding]]] = {}
        
        for agent_name, finding in all_findings:
            if not finding.evidence_ids:
                # Evidence가 없는 경우 별도로 "NO_EVIDENCE"에 적립
                evidence_dict.setdefault("NO_EVIDENCE", []).append((agent_name, finding))
            else:
                rep_id = finding.evidence_ids[0]
                evidence_dict.setdefault(rep_id, []).append((agent_name, finding))

        common_findings: List[AgentFinding] = []
        conflicts: List[ConflictingJudgment] = []

        for ev_id, group in evidence_dict.items():
            concurrent_count = len(set([a for a, _ in group]))
            
            if len(group) == 1:
                final_finding = self.risk_calculator.apply_context_aware_upgrades(
                    group[0][1], context, concurrent_count
                )
                common_findings.append(final_finding)
                continue

            # 동일 증거/상황 지적 사항 평가
            risk_levels = set([f.risk_level for _, f in group])
            is_conflict = (
                ("CRITICAL" in risk_levels or "HIGH" in risk_levels)
                and ("LOW" in risk_levels or "INFO" in risk_levels)
            )
            
            if is_conflict:
                issue_title = group[0][1].finding_title
                judgments = [
                    {"agent": agent, "view": f"{f.risk_level}: {f.finding_summary}"}
                    for agent, f in group
                ]
                agents_involved = list(set([agent for agent, _ in group]))
                
                conflict = ConflictingJudgment(
                    conflict_topic=f"위험성/정당성 판단 지표: {issue_title}",
                    agents_involved=agents_involved,
                    disagreement_reason=(
                        "어떤 철학 기반은 보수적 안전을, "
                        "어떤 기반은 사용자 자율성/자기형성을 우선으로 판단하여 상충"
                    ),
                    evidence_overlap=group[0][1].evidence_ids,
                    judgments=judgments,
                    arbiter_resolution=(
                        "고위험 정책 위반 가능성이 포함된 이상 안전을 선행 보장해야 "
                        "하므로 보수적 렌즈를 채택."
                    ),
                    residual_risk=(
                        "안전을 핑계로 한 권위주의적 자율성 억압"
                        "(니체/사르트르 지적)에 대한 서비스 차원의 잔존 리스크 존재."
                    ),
                )
                conflicts.append(conflict)
                
                # 상충 발생 시 가장 보수적 기준의 Finding 유지 (Context-aware Rule 적용)
                _c_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
                base_finding = sorted(
                    group, key=lambda x: _c_order.get(x[1].risk_level, 99)
                )[0][1]
                upgraded_finding = self.risk_calculator.apply_context_aware_upgrades(
                    base_finding, context, concurrent_count
                )
                common_findings.append(upgraded_finding)
            else:
                # 보수적으로 가장 강한 의견 병합 채택
                _risk_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
                base_finding = sorted(
                    group, key=lambda x: _risk_order.get(x[1].risk_level, 99)
                )[0][1]
                upgraded_finding = self.risk_calculator.apply_context_aware_upgrades(
                    base_finding, context, concurrent_count
                )
                
                all_principles = set()
                all_q_results = []
                all_h_reasons = []
                for _, f in group:
                    all_principles.update(f.violated_principles)
                    all_q_results.extend(f.question_results)
                    if f.human_review_reason:
                        all_h_reasons.append(f.human_review_reason)
                        
                upgraded_finding.violated_principles = list(all_principles)
                upgraded_finding.question_results = all_q_results[:5]  # 임의로 합침
                upgraded_finding.human_review_reason = " | ".join(all_h_reasons)
                common_findings.append(upgraded_finding)

        return common_findings, conflicts
