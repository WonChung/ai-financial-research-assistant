from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


DOCUMENTS_DIR = Path(__file__).resolve().parents[1] / "data" / "documents"


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    character_count: int
    created_at: str

app = FastAPI(title="AI Financial Research Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
) -> DocumentUploadResponse:
    filename = file.filename or ""

    if not filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported.")

    contents = await file.read()

    try:
        text = contents.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="Uploaded .txt files must be UTF-8 encoded.",
        ) from exc

    document_id = str(uuid4())
    created_at = datetime.now(UTC).isoformat()

    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    document_path = DOCUMENTS_DIR / f"{document_id}.txt"
    document_path.write_text(text, encoding="utf-8")

    return DocumentUploadResponse(
        document_id=document_id,
        filename=filename,
        character_count=len(text),
        created_at=created_at,
    )
