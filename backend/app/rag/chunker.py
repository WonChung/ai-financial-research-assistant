from typing import TypedDict

from app.rag.models import DocumentChunk, LoadedDocument


class TextChunk(TypedDict):
    chunk_index: int
    text: str
    start_char: int
    end_char: int


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[TextChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")

    if overlap < 0:
        raise ValueError("overlap must be greater than or equal to 0.")

    if overlap >= chunk_size:
        raise ValueError("overlap must be less than chunk_size.")

    if text == "":
        return []

    chunks: list[TextChunk] = []
    start_char = 0
    chunk_index = 0
    step = chunk_size - overlap

    while start_char < len(text):
        end_char = min(start_char + chunk_size, len(text))
        chunk = text[start_char:end_char]
        chunks.append(
            {
                "chunk_index": chunk_index,
                "text": chunk,
                "start_char": start_char,
                "end_char": end_char,
            }
        )

        if end_char == len(text):
            break

        start_char += step
        chunk_index += 1

    return chunks


def chunk_document(
    document: LoadedDocument,
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[DocumentChunk]:
    return [
        DocumentChunk(
            document_id=document.document_id,
            chunk_index=chunk["chunk_index"],
            text=chunk["text"],
            start_char=chunk["start_char"],
            end_char=chunk["end_char"],
            filename=document.filename,
        )
        for chunk in chunk_text(document.text, chunk_size=chunk_size, overlap=overlap)
    ]
