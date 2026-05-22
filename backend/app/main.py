from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.portfolio import Holding, summarize_portfolio_risk
from app.rag.document_loader import DocumentValidationError
from app.rag.pipeline import build_local_ingestion_service, build_local_rag_service


DOCUMENTS_DIR = Path(__file__).resolve().parents[1] / "data" / "documents"
CHUNKS_DIR = Path(__file__).resolve().parents[1] / "data" / "chunks"
VECTOR_STORE_PATH = Path(__file__).resolve().parents[1] / "data" / "vectors.json"


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    character_count: int
    created_at: str
    chunk_count: int


class AskRequest(BaseModel):
    document_id: str
    question: str
    top_k: int = 5


class CitationResponse(BaseModel):
    source_id: int
    document_id: str
    filename: str
    chunk_index: int
    start_char: int
    end_char: int


class AskResponse(BaseModel):
    answer: str
    citations: list[CitationResponse]


class PortfolioHoldingRequest(BaseModel):
    ticker: str
    name: str
    sector: str | None = None
    weight_percent: float


class PortfolioRiskSummaryRequest(BaseModel):
    holdings: list[PortfolioHoldingRequest]


class LargestPositionResponse(BaseModel):
    ticker: str
    name: str
    sector: str | None
    weight_percent: float


class PortfolioRiskSummaryResponse(BaseModel):
    concentration_risk_notes: list[str]
    largest_positions: list[LargestPositionResponse]
    sector_concentration_notes: list[str]
    missing_data_warnings: list[str]
    risk_explanation: str
    disclaimer: str


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

    document_id = str(uuid4())
    created_at = datetime.now(UTC).isoformat()
    ingestion_service = build_local_ingestion_service(
        documents_dir=DOCUMENTS_DIR,
        chunks_dir=CHUNKS_DIR,
        vector_store_path=VECTOR_STORE_PATH,
    )

    try:
        document, chunk_count = ingestion_service.ingest_txt(
            document_id=document_id,
            filename=filename,
            contents=contents,
            created_at=created_at,
        )
    except DocumentValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return DocumentUploadResponse(
        document_id=document.document_id,
        filename=document.filename,
        character_count=document.character_count,
        created_at=document.created_at,
        chunk_count=chunk_count,
    )


@app.post("/research/ask")
def ask_question(request: AskRequest) -> AskResponse:
    if not request.document_id.strip():
        raise HTTPException(status_code=400, detail="document_id is required.")

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="question is required.")

    if request.top_k <= 0:
        raise HTTPException(status_code=400, detail="top_k must be greater than 0.")

    rag_service = build_local_rag_service(VECTOR_STORE_PATH)
    generated_answer = rag_service.answer(
        document_id=request.document_id,
        question=request.question,
        top_k=request.top_k,
    )

    return AskResponse(
        answer=generated_answer.answer,
        citations=[
            CitationResponse(
                source_id=citation.source_id,
                document_id=citation.document_id,
                filename=citation.filename,
                chunk_index=citation.chunk_index,
                start_char=citation.start_char,
                end_char=citation.end_char,
            )
            for citation in generated_answer.citations
        ],
    )


@app.post("/portfolio/risk-summary")
def portfolio_risk_summary(
    request: PortfolioRiskSummaryRequest,
) -> PortfolioRiskSummaryResponse:
    if not request.holdings:
        raise HTTPException(status_code=400, detail="At least one holding is required.")

    holdings: list[Holding] = []
    for index, holding in enumerate(request.holdings, start=1):
        ticker = holding.ticker.strip().upper()
        name = holding.name.strip()
        sector = holding.sector.strip() if holding.sector else None

        if not ticker:
            raise HTTPException(
                status_code=400,
                detail=f"holding {index} ticker is required.",
            )

        if not name:
            raise HTTPException(
                status_code=400,
                detail=f"holding {index} name is required.",
            )

        if holding.weight_percent <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"holding {index} weight_percent must be greater than 0.",
            )

        holdings.append(
            Holding(
                ticker=ticker,
                name=name,
                sector=sector,
                weight_percent=holding.weight_percent,
            )
        )

    summary = summarize_portfolio_risk(holdings)
    return PortfolioRiskSummaryResponse(
        concentration_risk_notes=summary.concentration_risk_notes,
        largest_positions=[
            LargestPositionResponse(
                ticker=position.ticker,
                name=position.name,
                sector=position.sector,
                weight_percent=position.weight_percent,
            )
            for position in summary.largest_positions
        ],
        sector_concentration_notes=summary.sector_concentration_notes,
        missing_data_warnings=summary.missing_data_warnings,
        risk_explanation=summary.risk_explanation,
        disclaimer=summary.disclaimer,
    )
