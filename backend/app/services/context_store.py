import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class StoredFile:
    file_id: str
    filename: str
    content_type: str
    extracted_text: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ContextStore:
    """In-memory upload store for Phase 2 (replace with DB/S3 in Phase 7)."""

    def __init__(self) -> None:
        self._files: dict[str, StoredFile] = {}

    def save(self, filename: str, content_type: str, extracted_text: str) -> StoredFile:
        file_id = str(uuid.uuid4())
        record = StoredFile(
            file_id=file_id,
            filename=filename,
            content_type=content_type,
            extracted_text=extracted_text,
        )
        self._files[file_id] = record
        return record

    def get(self, file_id: str) -> StoredFile | None:
        return self._files.get(file_id)

    def get_many(self, file_ids: list[str]) -> list[StoredFile]:
        return [self._files[fid] for fid in file_ids if fid in self._files]


context_store = ContextStore()
