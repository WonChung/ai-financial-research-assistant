from app.rag.models import LoadedDocument


class DocumentValidationError(ValueError):
    pass


def load_txt_document(
    *,
    document_id: str,
    filename: str,
    contents: bytes,
    created_at: str,
) -> LoadedDocument:
    if not filename.lower().endswith(".txt"):
        raise DocumentValidationError("Only .txt files are supported.")

    try:
        text = contents.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DocumentValidationError(
            "Uploaded .txt files must be UTF-8 encoded."
        ) from exc

    return LoadedDocument(
        document_id=document_id,
        filename=filename,
        text=text,
        created_at=created_at,
    )
