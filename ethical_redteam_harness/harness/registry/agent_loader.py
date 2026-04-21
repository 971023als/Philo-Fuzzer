import os
import json
import yaml
from typing import Dict, List, Any, Optional
from harness.schemas.models import PhilosopherProfile

class PhiloAgent:
    def __init__(self, name: str, folder_path: str):
        self.name = name
        self.folder_path = folder_path
        self.prompt_template = ""
        self.checklist: Dict[str, Any] = {}
        self.schema: Dict[str, Any] = {}
        self.principles: str = ""
        self.scoring_rules: Dict[str, Any] = {}
        self.persona_profile: Optional[PhilosopherProfile] = None
        
    def load(self):
        """에이전트 폴더 내의 필수 파일들을 로드합니다."""
        # 1. Prompt
        with open(os.path.join(self.folder_path, "prompt.md"), "r", encoding="utf-8") as f:
            self.prompt_template = f.read()
            
        # 2. Principles
        with open(os.path.join(self.folder_path, "principles.md"), "r", encoding="utf-8") as f:
            self.principles = f.read()

        # 3. Checklist
        with open(os.path.join(self.folder_path, "checklist.yaml"), "r", encoding="utf-8") as f:
            self.checklist = yaml.safe_load(f)

        # 4. Schema
        with open(os.path.join(self.folder_path, "schema.json"), "r", encoding="utf-8") as f:
            self.schema = json.load(f)

        # 5. Structured philosopher persona
        with open(os.path.join(self.folder_path, "persona.yaml"), "r", encoding="utf-8") as f:
            self.persona_profile = PhilosopherProfile.model_validate(yaml.safe_load(f))

        # 6. Scoring (Optional but recommended)
        scoring_path = os.path.join(self.folder_path, "scoring.yaml")
        if os.path.exists(scoring_path):
            with open(scoring_path, "r", encoding="utf-8") as f:
                self.scoring_rules = yaml.safe_load(f)

class AgentLoader:
    def __init__(self, agents_dir: str = "agents"):
        self.agents_dir = agents_dir
        self.agents: Dict[str, PhiloAgent] = {}
        
    def discover_and_load(self) -> List[str]:
        """agents 디렉터리를 스캔하여 유효한 철학자 에이전트를 로드합니다."""
        if not os.path.exists(self.agents_dir):
            os.makedirs(self.agents_dir, exist_ok=True)
            return []

        loaded_names = []
        for entry in os.listdir(self.agents_dir):
            full_path = os.path.join(self.agents_dir, entry)
            if os.path.isdir(full_path):
                if self._is_valid_agent_folder(full_path):
                    agent = PhiloAgent(name=entry, folder_path=full_path)
                    agent.load()
                    self.agents[entry] = agent
                    loaded_names.append(entry)
                else:
                    print(f"[Warning] Invalid agent folder omitted: {entry}")
                    
        return loaded_names

    def _is_valid_agent_folder(self, folder_path: str) -> bool:
        """해당 폴더가 요구사항의 4대 필수 파일을 모두 가지고 있는지 검증합니다."""
        required_files = ["prompt.md", "checklist.yaml", "schema.json", "principles.md", "persona.yaml"]
        return all(os.path.exists(os.path.join(folder_path, f)) for f in required_files)

    def get_agent(self, name: str) -> Optional[PhiloAgent]:
        """이름으로 에이전트를 가져옵니다."""
        return self.agents.get(name)

    def get_all_agents(self) -> List[PhiloAgent]:
        """arbiter를 제외한 평가용 에이전트 리스트를 반환합니다."""
        return [agent for name, agent in self.agents.items() if name != "arbiter"]
        
    def get_arbiter(self) -> Optional[PhiloAgent]:
        """총괄 심사(arbiter) 에이전트를 반환합니다."""
        return self.agents.get("arbiter")
