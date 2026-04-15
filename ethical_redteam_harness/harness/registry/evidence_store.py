import os
import json
import hashlib
from datetime import datetime
from typing import List, Optional, Dict, Any
from harness.schemas.models import EvidenceRecord

class EvidenceStore:
    def __init__(self, base_dir: str = "evidence"):
        """증거 저장소 초기화. 기본 경로는 evidence 폴더입니다."""
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        self._cache: Dict[str, EvidenceRecord] = {}

    def _generate_id(self, source_ref: str, content: str) -> str:
        """내용 기반의 해시 문자열을 결합하여 고유 evidence_id를 생성합니다."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:6]
        return f"EV-{timestamp}-{content_hash}"

    def create_evidence(self, run_id: str, source_type: str, source_ref: str, summary: str, content: str, tags: List[str] = None, parent_ids: List[str] = None) -> str:
        """새로운 증거를 생성하고 저장소에 기록합니다."""
        evidence_id = self._generate_id(source_ref, content)
        record = EvidenceRecord(
            evidence_id=evidence_id,
            run_id=run_id,
            source_type=source_type,
            source_ref=source_ref,
            summary=summary,
            content=content,
            tags=tags or [],
            parent_evidence_ids=parent_ids or []
        )
        self._save(record)
        return evidence_id

    def _save(self, record: EvidenceRecord):
        """단일 Proof Record를 JSON으로 저장합니다."""
        self._cache[record.evidence_id] = record
        file_path = os.path.join(self.base_dir, f"{record.evidence_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(record.model_dump_json(indent=2))

    def get_evidence(self, evidence_id: str) -> Optional[EvidenceRecord]:
        """주어진 ID로 증거를 조회합니다."""
        if evidence_id in self._cache:
            return self._cache[evidence_id]
            
        file_path = os.path.join(self.base_dir, f"{evidence_id}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                record = EvidenceRecord.model_validate(data)
                self._cache[evidence_id] = record
                return record
        return None

    def list_all_evidence(self) -> List[EvidenceRecord]:
        """저장된 모든 증거를 반환합니다."""
        records = []
        for filename in os.listdir(self.base_dir):
            if filename.endswith(".json"):
                ev_id = filename.replace(".json", "")
                record = self.get_evidence(ev_id)
                if record:
                    records.append(record)
        return records
