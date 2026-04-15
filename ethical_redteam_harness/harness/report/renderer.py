import os
import json
from harness.schemas.models import ArbiterOutputSchema

MARKDOWN_TEMPLATE = """# 철학자 기반 AI 윤리 레드팀 평가 보고서

## 1. 평가 개요
- **최종 위험도 점수**: {{ overall_risk_score }} / 100
- **종합 신뢰도**: {{ overall_confidence }}
- **경영진 요약 (Executive Summary)**:
{{ executive_summary }}

## 2. 우선 조치 권고 (Top Risks & Actions)
{% for action in priority_actions %}
- {{ action }}
{% endfor %}

## 3. 공통 윤리 취약점 (Common Findings)
{% for finding in common_findings %}
### [{{ finding.risk_level }}] {{ finding.finding_title }} (Confidence: {{ finding.confidence }})
- **Summary**: {{ finding.finding_summary }}
- **Evidence IDs**: {{ finding.evidence_ids | join(', ') }}
- **Violated Principles**: {{ finding.violated_principles | join(', ') }}
- **Counter Argument**: {{ finding.counter_argument }}
- **Recommendations**:
{% for rec in finding.recommended_actions %}  - {{ rec }}
{% endfor %}
{% endfor %}

## 4. 상충 판단 분석 (Conflicting Judgments)
{% for conflict in conflicting_judgments %}
### {{ conflict.issue }}
- **Synthesis (병합 의견)**: {{ conflict.synthesis }}
- **세부 의견 목록**:
{% for judge in conflict.judgments %}  - **{{ judge.agent }}**: {{ judge.view }}
{% endfor %}
{% endfor %}

## 5. 재시험 기준
{% for criteria in retest_criteria %}
- {{ criteria }}
{% endfor %}

## 6. 결론 (Final Opinion)
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
