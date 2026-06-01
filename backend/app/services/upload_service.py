from io import BytesIO

from fastapi import UploadFile

from app.errors import AppError
from app.services.context_store import StoredFile, context_store

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf"}
ALLOWED_MIME = {
    "text/plain",
    "text/markdown",
    "application/pdf",
    "application/x-pdf",
}


async def extract_text(filename: str, content_type: str, data: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise AppError(
                "PDF_UNSUPPORTED",
                "PDF extraction requires pypdf on the server",
                500,
            ) from exc
        reader = PdfReader(BytesIO(data))
        parts = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(parts).strip()

    if lower.endswith((".txt", ".md")) or content_type in ("text/plain", "text/markdown"):
        return data.decode("utf-8", errors="replace").strip()

    raise AppError(
        "INVALID_UPLOAD",
        f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        400,
    )


async def save_upload(file: UploadFile) -> StoredFile:
    if not file.filename:
        raise AppError("INVALID_UPLOAD", "filename is required", 400)

    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise AppError(
            "INVALID_UPLOAD",
            f"Unsupported extension '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            400,
        )

    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_MIME and ext not in ALLOWED_EXTENSIONS:
        raise AppError("INVALID_UPLOAD", f"Unsupported MIME type: {content_type}", 400)

    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise AppError("INVALID_UPLOAD", "File exceeds 10MB limit", 400)

    text = await extract_text(file.filename, content_type, data)
    return context_store.save(file.filename, content_type, text)
