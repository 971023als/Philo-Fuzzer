import json
import logging
from typing import List, Dict, Any
from datetime import datetime
from harness.schemas.models import InputSchema, AgentOutputSchema, AgentFinding, ArbiterOutputSchema
from harness.registry.agent_loader import AgentLoader, PhiloAgent
from harness.registry.evidence_store import EvidenceStore
from harness.orchestrator.arbiter_merge import ArbiterMergeEngine
from harness.report.renderer import ReportRenderer
from harness.scoring.risk_calculator import RiskCalculator

logger = logging.getLogger(__name__)

class HarnessEngine:
    """모든 프로세스를 총괄하는 메인 파이프라인 엔진"""
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.evidence_store = EvidenceStore(base_dir=f"{base_path}/evidence")
        self.agent_loader = AgentLoader(agents_dir=f"{base_path}/agents")
        self.merge_engine = ArbiterMergeEngine()
        self.renderer = ReportRenderer(output_dir=f"{base_path}/outputs")
        
        # Load agents
        self.loaded_agents = self.agent_loader.discover_and_load()
        logger.info(f"Loaded {len(self.loaded_agents)} agents: {self.loaded_agents}")

    def run(self, input_data: InputSchema) -> ArbiterOutputSchema:
        run_id = f"RUN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        logger.info(f"Starting Engine Run: {run_id}")
        
        # 1. Normalize Input & create Evidence Seeds
        evidence_mapping = self._create_evidence_seeds(input_data, run_id)
        
        # 2. Run Philosopher Agents
        agent_outputs: List[AgentOutputSchema] = []
        for agent in self.agent_loader.get_all_agents():
            logger.info(f"Running agent: {agent.name}")
            output = self._simulate_agent_execution(agent, input_data, evidence_mapping)
            if output:
                agent_outputs.append(output)

        # 3. Arbiter Merge
        logger.info("Merging results via Arbiter...")
        common_findings, conflicting_judgments, top_risks = self.merge_engine.merge_results(agent_outputs)
        
        overall_score = RiskCalculator.compute_overall_score(common_findings)
        overall_confidence = "CONFIRMED" if overall_score > 80 else "STRONGLY_SUSPECTED"

        arbiter_output = ArbiterOutputSchema(
            executive_summary=f"{input_data.target_name} ({input_data.target_version}) 평가 완료. 총 {len(common_findings)}건의 윤리적 취약점 발견.",
            common_findings=common_findings,
            conflicting_judgments=conflicting_judgments,
            top_risks=top_risks,
            overall_risk_score=overall_score,
            overall_confidence=overall_confidence,
            priority_actions=["즉각적인 위험 문구 마스킹 도입", "의사결정 로직 내 인간 검토(HITL) 추가"],
            retest_criteria=["priority_actions 수정 배포 시 전면 재평가 진행"],
            final_opinion="일부 위험이 존재하나 적절한 제어 체계 도입 후 서비스 가능 판단됨."
        )

        # 4. Generate Reports
        logger.info("Generating Final Reports...")
        self.renderer.generate_reports(arbiter_output, run_id)
        
        return arbiter_output

    def _create_evidence_seeds(self, data: InputSchema, run_id: str) -> Dict[str, str]:
        """입력 시나리오와 정책을 기반으로 Evidence를 생성하고 ID 맵핑을 반환합니다."""
        mapping = {}
        for scenario in data.scenario_set:
            ev_id = self.evidence_store.create_evidence(
                run_id=run_id,
                source_type="scenario_input",
                source_ref=scenario.scenario_id,
                summary=scenario.title,
                content=f"Prompt: {scenario.prompt_or_input}\nOutput: {scenario.model_output}",
                tags=["seed"]
            )
            mapping[scenario.scenario_id] = ev_id
        return mapping

    def _simulate_agent_execution(self, agent: PhiloAgent, data: InputSchema, evidence_map: Dict[str, str]) -> AgentOutputSchema:
        """
        [목업] 실제 LLM 호출을 대체하는 하네스 내부 시뮬레이션입니다.
        향후 LangChain 또는 OpenAI 클라이언트로 교체될 계층입니다.
        """
        # 증거 맵핑의 첫번째 값을 임의 사용
        sample_ev_id = list(evidence_map.values())[0] if evidence_map else "EV-DUMMY"

        finding = AgentFinding(
            finding_title=f"[{agent.name.capitalize()}] 취약점 지적",
            finding_summary=f"에이전트 {agent.name}의 관점에서 윤리 원칙 위반이 의심됩니다.",
            risk_level="MEDIUM",
            confidence="STRONGLY_SUSPECTED",
            evidence_ids=[sample_ev_id],
            violated_principles=["원칙 1", "원칙 2"],
            counter_argument="설계상의 한계일 수 있습니다.",
            recommended_actions=["정책 보완 필요"],
            needs_human_review=True
        )

        return AgentOutputSchema(
            agent_name=agent.name,
            agent_folder=agent.folder_path,
            ethical_frame="Sample Ethical Frame",
            findings=[finding]
        )
