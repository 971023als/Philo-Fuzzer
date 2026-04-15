from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# ==============================================================================
# 1. Input Schemas (입력 스키마)
# ==============================================================================

class RiskContext(BaseModel):
    high_risk: bool = Field(default=False, description="고위험 도메인 여부")
    sensitive_data: bool = Field(default=False, description="민감 정보 취급 여부")
    user_type: str = Field(default="general", description="사용자 유형 (예: 일반, 미성년자, 취약계층 등)")

class Scenario(BaseModel):
    scenario_id: str
    title: str
    description: str
    prompt_or_input: str
    model_output: str
    expected_guardrails: List[str] = Field(default_factory=list)

class PolicyRef(BaseModel):
    policy_id: str
    title: str
    excerpt: str

class IORecord(BaseModel):
    request: str
    response: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

class Constraints(BaseModel):
    language: str = Field(default="ko")
    report_format: List[str] = Field(default_factory=lambda: ["json", "md", "html"])

class InputSchema(BaseModel):
    target_name: str
    target_version: str
    evaluation_goal: str
    service_domain: str
    risk_context: RiskContext
    scenario_set: List[Scenario]
    policy_references: List[PolicyRef] = Field(default_factory=list)
    conversation_or_io_records: List[IORecord] = Field(default_factory=list)
    review_scope: List[str] = Field(default_factory=list)
    constraints: Constraints = Field(default_factory=Constraints)


# ==============================================================================
# 2. Evidence Registry Schemas (증거 레지스트리 스키마)
# ==============================================================================

class EvidenceRecord(BaseModel):
    evidence_id: str
    schema_version: str = Field(default="1.0")
    run_id: str
    source_type: Literal["scenario_input", "model_output", "policy_excerpt", "derived_claim"]
    source_ref: str
    summary: str
    content: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    tags: List[str] = Field(default_factory=list)
    parent_evidence_ids: List[str] = Field(default_factory=list)


# ==============================================================================
# 3. Agent Output Schemas (개별 철학자 에이전트 출력 스키마)
# ==============================================================================

ConfidenceLevel = Literal["CONFIRMED", "STRONGLY_SUSPECTED", "NEEDS_VERIFICATION"]
RiskLevel = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]

class AgentFinding(BaseModel):
    finding_id: Optional[str] = None
    finding_title: str
    finding_summary: str
    risk_level: RiskLevel
    confidence: ConfidenceLevel
    evidence_ids: List[str]
    violated_principles: List[str] = Field(default_factory=list)
    counter_argument: str = Field(default="")
    recommended_actions: List[str] = Field(default_factory=list)
    needs_human_review: bool = Field(default=False)

class AgentOutputSchema(BaseModel):
    agent_name: str
    agent_folder: str
    ethical_frame: str
    findings: List[AgentFinding]


# ==============================================================================
# 4. Arbiter Output Schemas (총괄 심사 출력 스키마)
# ==============================================================================

class ConflictingJudgment(BaseModel):
    issue: str
    judgments: List[Dict[str, str]]  # e.g., [{"agent": "socrates", "view": "..."}]
    synthesis: str

class ArbiterOutputSchema(BaseModel):
    executive_summary: str
    common_findings: List[AgentFinding]
    conflicting_judgments: List[ConflictingJudgment] = Field(default_factory=list)
    top_risks: List[str] = Field(default_factory=list)
    overall_risk_score: float = Field(ge=0, le=100)
    overall_confidence: ConfidenceLevel
    priority_actions: List[str] = Field(default_factory=list)
    retest_criteria: List[str] = Field(default_factory=list)
    final_opinion: str
