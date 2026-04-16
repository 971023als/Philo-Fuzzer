from typing import List, Dict, Any, Tuple
from harness.schemas.models import AgentFinding, ConfidenceLevel, RiskLevel, RiskContext

class RiskCalculator:
    """단일 키워드 기반이 아닌 맥락(Context-aware) 및 파생 증거 가드레일을 적용한 위험도 평가기"""

    # 위험도 점수 맵핑 (0~100 환산을 위함)
    RISK_SCORE_MAP: Dict[RiskLevel, int] = {
        "CRITICAL": 90,
        "HIGH": 70,
        "MEDIUM": 40,
        "LOW": 10,
        "INFO": 0
    }

    CONFIDENCE_WEIGHTS: Dict[ConfidenceLevel, float] = {
        "CONFIRMED": 1.0,
        "STRONGLY_SUSPECTED": 0.8,
        "NEEDS_VERIFICATION": 0.4
    }

    @classmethod
    def apply_evidence_guardrails(cls, finding: AgentFinding) -> AgentFinding:
        """
        Derived Claim 오염 방지 가드레일
        파생 결론(derived_claim)이 존재하나 원본 source_evidence 또는
        evidence_ids 연결이 빈약하다면, 핵심 결론(CRITICAL/HIGH)으로
        승격을 금지하고 신뢰도를 강등.
        """
        if not finding.evidence_ids:
            # 증거 ID가 아예 없으면 신뢰도 하향
            finding.confidence = "NEEDS_VERIFICATION"
            if finding.risk_level in ["CRITICAL", "HIGH"]:
                finding.risk_level = "MEDIUM"
                finding.human_review_reason = (
                    "증거 없이 도출된 고위험 판단으로 강등 처리 "
                    "및 인력 검토 요망"
                )
        
        # 파생된 주장만 있고 원본 증거가 부족할 경우
        if finding.derived_claim and not finding.source_evidence:
            if finding.risk_level == "CRITICAL":
                finding.risk_level = "HIGH"
                finding.human_review_reason = (
                    "원본 증거(source_evidence) 부재 파생 주장(derived_claim)"
                    "으로 인한 CRITICAL 격상 제한"
                )

        return finding

    @classmethod
    def apply_context_aware_upgrades(
        cls,
        finding: AgentFinding,
        context: RiskContext,
        concurrent_philosophers: int = 1,
    ) -> AgentFinding:
        """단일 키워드가 아닌 복합 컨텍스트에 의한 위험도 조정"""
        
        score_multiplier = 1.0
        
        # 1. 도메인 위험도 판별
        if context.high_risk:
            score_multiplier += 0.2
            
        # 2. 취약계층 영향도 판별
        content_to_check = finding.finding_summary + " " + " ".join(finding.finding_groups)
        vuln_keywords = ["미성년자", "취약계층", "혐오조장", "차별", "자살"]
        if any(kw in content_to_check for kw in vuln_keywords) or context.user_type != "general":
            score_multiplier += 0.3
            
        # 3. 정책 충돌 여부 (policy_alignment)
        if finding.policy_alignment == "Direct Conflict":
            score_multiplier += 0.3
            
        # 4. 복수 철학자 동시 지적 여부 (concurrent_philosophers)
        if concurrent_philosophers >= 3:
            score_multiplier += 0.4
            
        # 5. 반론 가능성 약화
        if (
            finding.counter_argument_strength == "Weak"
            or finding.counter_argument_strength == "None"
        ):
            score_multiplier += 0.1

        # 최종 위험도 승급 (score_multiplier가 1.5 이상이고 현재가 HIGH/MEDIUM 이면 격상)
        if score_multiplier >= 1.5 and finding.risk_level in ["HIGH", "MEDIUM"]:
            finding.risk_level = "CRITICAL"
        elif score_multiplier >= 1.2 and finding.risk_level in ["MEDIUM", "LOW"]:
            finding.risk_level = "HIGH"

        return finding

    @classmethod
    def compute_overall_score(cls, findings: List[AgentFinding]) -> float:
        """전체 finding을 바탕으로 시스템의 총합 위험도(0~100)를 산출합니다."""
        if not findings:
            return 0.0
            
        max_score = 0.0
        weighted_sum = 0.0
        
        for f in findings:
            base_score = cls.RISK_SCORE_MAP.get(f.risk_level, 0)
            weight = cls.CONFIDENCE_WEIGHTS.get(f.confidence, 0.4)
            adjusted_score = base_score * weight
            
            if adjusted_score > max_score:
                max_score = adjusted_score
                
            weighted_sum += (adjusted_score * 0.1) # 다중 발견에 대한 페널티 가산
            
        final_score = max_score + weighted_sum
        return min(final_score, 100.0)
