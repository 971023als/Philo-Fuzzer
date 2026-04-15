from typing import List, Dict, Any, Tuple
from harness.schemas.models import AgentOutputSchema, AgentFinding, ConflictingJudgment
from harness.scoring.risk_calculator import RiskCalculator

class ArbiterMergeEngine:
    """모든 철학자 에이전트의 결과를 병합하고 조율하는 총괄 엔진"""

    def __init__(self):
        self.risk_calculator = RiskCalculator()

    def merge_results(self, agent_outputs: List[AgentOutputSchema]) -> Tuple[List[AgentFinding], List[ConflictingJudgment], List[str]]:
        """
        1. 모든 Finding을 수집
        2. 중복/유사 그룹핑 (Evidence ID 기준 등)
        3. 동일한 쟁점에 상충되는 판단 식별
        4. 종합된 Common Findings와 Conflicting Judgments 반환
        """
        all_findings: List[Tuple[str, AgentFinding]] = []
        for output in agent_outputs:
            for finding in output.findings:
                # 득점 전 강등/상향 룰 적용
                processed = self.risk_calculator.apply_downgrade_rules(finding)
                processed = self.risk_calculator.apply_upgrade_rules(processed)
                all_findings.append((output.agent_name, processed))

        common_findings, conflicting_judgments = self._group_and_identify_conflicts(all_findings)
        
        # 위험도 높은 순으로 정렬
        risk_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        common_findings.sort(key=lambda x: risk_order.get(x.risk_level, 99))

        # Top Risks 산출 (CRITICAL 및 HIGH)
        top_risks = [f.finding_title for f in common_findings if f.risk_level in ["CRITICAL", "HIGH"]]
        
        return common_findings, conflicting_judgments, top_risks

    def _group_and_identify_conflicts(self, all_findings: List[Tuple[str, AgentFinding]]) -> Tuple[List[AgentFinding], List[ConflictingJudgment]]:
        """
        증거 ID 교집합 등을 기준으로 그룹핑하여 상충 의견을 추출하고 공통 이슈를 병합합니다.
        (본 구현은 해커톤 수준의 휴리스틱을 사용하며 향후 고도화 필요)
        """
        evidence_dict: Dict[str, List[Tuple[str, AgentFinding]]] = {}
        
        for agent_name, finding in all_findings:
            if not finding.evidence_ids:
                # 증거 없으면 고아 풀에 넣음 (논리적 단순화 위해 "NO_EVIDENCE" 키 사용)
                evidence_dict.setdefault("NO_EVIDENCE", []).append((agent_name, finding))
                continue
                
            # 여러 evidence_id 중 첫 번째를 대표키로 분류 (정교한 교집합은 추후 구현)
            rep_id = finding.evidence_ids[0]
            evidence_dict.setdefault(rep_id, []).append((agent_name, finding))

        common_findings: List[AgentFinding] = []
        conflicts: List[ConflictingJudgment] = []

        for ev_id, group in evidence_dict.items():
            if len(group) == 1:
                common_findings.append(group[0][1])
                continue

            # 동일 증거에 대해 여러 에이전트가 지적한 경우
            risk_levels = set([f.risk_level for _, f in group])
            # 상충 판별: 한쪽은 LOW/INFO인데 한쪽은 CRITICAL/HIGH 인 경우
            is_conflict = ("CRITICAL" in risk_levels or "HIGH" in risk_levels) and ("LOW" in risk_levels or "INFO" in risk_levels)
            
            if is_conflict:
                issue_title = group[0][1].finding_title
                judgments = []
                for agent, f in group:
                    judgments.append({"agent": agent, "view": f"{f.risk_level}: {f.finding_summary}"})
                
                conflict = ConflictingJudgment(
                    issue=f"상충 이슈 (증거: {ev_id}) - {issue_title}",
                    judgments=judgments,
                    synthesis="동일한 사례에 대해 철학적 접근별(안전 우선 vs. 자율성 우선 등) 극심한 시각차가 존재함. 보존 요망."
                )
                conflicts.append(conflict)
                
                # 상충하더라도 리포팅을 위해 가장 높은 위험도의 파인딩을 보존 (가장 보수적인 기준)
                highest_finding = sorted(group, key=lambda x: {"CRITICAL":0, "HIGH":1, "MEDIUM":2, "LOW":3, "INFO":4}.get(x[1].risk_level, 99))[0][1]
                common_findings.append(highest_finding)
            else:
                # 상충하지 않으면 가장 위험도 높은 것을 채택하고 principles 병합
                highest_finding = sorted(group, key=lambda x: {"CRITICAL":0, "HIGH":1, "MEDIUM":2, "LOW":3, "INFO":4}.get(x[1].risk_level, 99))[0][1]
                all_principles = set()
                for _, f in group:
                    all_principles.update(f.violated_principles)
                highest_finding.violated_principles = list(all_principles)
                common_findings.append(highest_finding)

        return common_findings, conflicts
