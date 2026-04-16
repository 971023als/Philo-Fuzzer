from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# ==============================================================================
# 1. Input Schemas
# ==============================================================================

class RiskContext(BaseModel):
    high_risk: bool = Field(default=False)
    sensitive_data: bool = Field(default=False)
    user_type: str = Field(default="general")

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
# 2. Evidence Registry Schemas
# ==============================================================================

class EvidenceRecord(BaseModel):
    evidence_id: str
    schema_version: str = Field(default="2.0")
    run_id: str
    source_type: Literal["scenario_input", "model_output", "policy_excerpt", "derived_claim"]
    evidence_tier: Literal[
        "source_evidence",
        "derived_evidence",
        "agent_interpretation",
        "arbiter_summary",
    ]
    source_ref: str
    summary: str
    content: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    tags: List[str] = Field(default_factory=list)
    parent_evidence_ids: List[str] = Field(default_factory=list) # Derived Claim에서 필수적

# ==============================================================================
# 3. Agent Output Schemas
# ==============================================================================

ConfidenceLevel = Literal["CONFIRMED", "STRONGLY_SUSPECTED", "NEEDS_VERIFICATION"]
RiskLevel = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]

class QuestionResult(BaseModel):
    question_id: str
    passed: bool
    rationale: str

class PrincipleScore(BaseModel):
    principle_name: str
    weight: float

class AgentFinding(BaseModel):
    finding_id: Optional[str] = None
    finding_title: str
    finding_summary: str
    finding_groups: List[str] = Field(default_factory=list)
    risk_level: RiskLevel
    confidence: ConfidenceLevel
    evidence_ids: List[str]                  
    source_evidence: List[str] = Field(default_factory=list)   # 원본 증거 매핑 명시
    derived_claim: List[str] = Field(default_factory=list)     # 파생 해석 명시
    finding_origin: str = Field(default="agent")
    evidence_strength: str = Field(default="High")
    question_results: List[QuestionResult] = Field(default_factory=list)
    principle_scores: Dict[str, float] = Field(default_factory=dict)
    violated_principles: List[str] = Field(default_factory=list)
    counter_argument: str = Field(default="")
    counter_argument_strength: Literal["Weak", "Medium", "Strong", "None"] = Field(default="None")
    recommended_actions: List[str] = Field(default_factory=list)
    policy_alignment: str = Field(default="N/A") 
    needs_human_review: bool = Field(default=False)
    human_review_reason: str = Field(default="")

class AgentOutputSchema(BaseModel):
    agent_name: str
    agent_folder: str
    ethical_frame: str
    findings: List[AgentFinding]

# ==============================================================================
# 4. Arbiter Output Schemas
# ==============================================================================

class ConflictingJudgment(BaseModel):
    conflict_topic: str
    agents_involved: List[str]
    disagreement_reason: str
    evidence_overlap: List[str]
    judgments: List[Dict[str, str]]
    arbiter_resolution: str
    residual_risk: str

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
