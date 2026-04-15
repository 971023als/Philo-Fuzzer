import os
from harness.schemas.models import ArbiterOutputSchema

MARKDOWN_TEMPLATE = """# 철학자 기반 AI 윤리 레드팀 평가 보고서

## 1. 평가 개요
- **최종 위험도 점수**: {{ overall_risk_score }} / 100
- **종합 신뢰도**: {{ overall_confidence }}
- **경영진 요약 (Executive Summary)**:
{{ executive_summary }}

## 2. 우선 조치 권고 (Top Risks & Actions)
|순위|위험 요소|권고사항|
|---|---|---|
{% for action in priority_actions %}|{{ loop.index }}|핵심 정책 위반 대응|{{ action }}|
{% endfor %}

## 3. 철학자별 Finding 요약 표 (Common Findings)
|Risk|Title|Groups|Evidence Link|Confidence|Human Review|
|---|---|---|---|---|---|
{% for f in common_findings %}|**{{ f.risk_level }}**|{{ f.finding_title }}|{{ f.finding_groups | join(', ') }}|{{ f.evidence_ids | join(', ') }} (Strength: {{ f.evidence_strength }})|{{ f.confidence }}|{% if f.needs_human_review %}Yes ({{ f.human_review_reason }}){% else %}No{% endif %}|
{% endfor %}

### 3.1 상세 취약점 분석 내역
{% for f in common_findings %}
#### [{{ f.risk_level }}] {{ f.finding_title }}
- **분리된 증거 계층 추적**:
  - `Source Evidence`: {{ f.source_evidence | join(', ') if f.source_evidence else 'N/A' }}
  - `Derived Claim`: {{ f.derived_claim | join(', ') if f.derived_claim else 'N/A' }} 
- **정책 정렬 충돌도 (Policy Alignment)**: {{ f.policy_alignment }}
- **Violated Principles**: {{ f.violated_principles | join(', ') }}
- **의견 및 논거**: 
  - Summary: {{ f.finding_summary }}
  - Counter Argument [Strength: **{{ f.counter_argument_strength }}**]: {{ f.counter_argument }}
- **권고 조치 (Recommendations)**:
{% for rec in f.recommended_actions %}  - {{ rec }}{% endfor %}

{% endfor %}

## 4. 상충 판단 표 (Conflicting Judgments)
|Conflict Topic|Agents Involved|Disagreement Reason|Evidence|Arbiter Resolution|Residual Risk|
|---|---|---|---|---|---|
{% for conflict in conflicting_judgments %}|**{{ conflict.conflict_topic }}**|{{ conflict.agents_involved | join(', ') }}|{{ conflict.disagreement_reason }}|{{ conflict.evidence_overlap | join(', ') }}|{{ conflict.arbiter_resolution }}|{{ conflict.residual_risk }}|
{% endfor %}

### 4.1 상충 판단 세부 진영
{% for conflict in conflicting_judgments %}
#### {{ conflict.conflict_topic }} 상세 대립
{% for judge in conflict.judgments %}  - **{{ judge.agent }}**: {{ judge.view }}
{% endfor %}
{% endfor %}

## 5. 재시험 기준 표 (Retest Criteria)
|재시험 항목|기준 조건|
|---|---|
{% for criteria in retest_criteria %}|시나리오 검증|{{ criteria }}|
{% endfor %}

## 6. 한계 및 유보 사항 (Final Opinion)
{{ final_opinion }}
"""

class ReportRenderer:
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_reports(self, arbiter_output: ArbiterOutputSchema, run_id: str):
        # JSON 생성
        json_path = os.path.join(self.output_dir, f"report_{run_id}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(arbiter_output.model_dump_json(indent=2))

        # 내부적으로 Jinja2 의존성을 줄이기 위해 단순 string replace 템플릿 엔진 흉내 (실제로는 jinja2 사용권장)
        md_content = self._render_markdown_basic(arbiter_output)
        md_path = os.path.join(self.output_dir, f"report_{run_id}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
            
        print(f"Reports successfully generated in {self.output_dir} with id {run_id}")

    def _render_markdown_basic(self, data: ArbiterOutputSchema) -> str:
        # Jinja2가 없어도 동작하기 위한 초간단 렌더링 로직 (Prototype 용)
        import jinja2
        template = jinja2.Template(MARKDOWN_TEMPLATE)
        return template.render(
            overall_risk_score=data.overall_risk_score,
            overall_confidence=data.overall_confidence,
            executive_summary=data.executive_summary,
            priority_actions=data.priority_actions,
            common_findings=data.common_findings,
            conflicting_judgments=data.conflicting_judgments,
            retest_criteria=data.retest_criteria,
            final_opinion=data.final_opinion
        )
