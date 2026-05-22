import pytest

from app.rag.chunker import chunk_text


def test_chunk_text_returns_single_chunk_for_short_text() -> None:
    assert chunk_text("abcdef", chunk_size=10, overlap=2) == [
        {
            "chunk_index": 0,
            "text": "abcdef",
            "start_char": 0,
            "end_char": 6,
        }
    ]


def test_chunk_text_splits_text_with_overlap() -> None:
    chunks = chunk_text("abcdefghijkl", chunk_size=5, overlap=2)

    assert chunks == [
        {
            "chunk_index": 0,
            "text": "abcde",
            "start_char": 0,
            "end_char": 5,
        },
        {
            "chunk_index": 1,
            "text": "defgh",
            "start_char": 3,
            "end_char": 8,
        },
        {
            "chunk_index": 2,
            "text": "ghijk",
            "start_char": 6,
            "end_char": 11,
        },
        {
            "chunk_index": 3,
            "text": "jkl",
            "start_char": 9,
            "end_char": 12,
        },
    ]


def test_chunk_text_returns_no_chunks_for_empty_text() -> None:
    assert chunk_text("") == []


@pytest.mark.parametrize(
    ("chunk_size", "overlap", "message"),
    [
        (0, 0, "chunk_size must be greater than 0."),
        (10, -1, "overlap must be greater than or equal to 0."),
        (10, 10, "overlap must be less than chunk_size."),
    ],
)
def test_chunk_text_validates_settings(
    chunk_size: int,
    overlap: int,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        chunk_text("abcdef", chunk_size=chunk_size, overlap=overlap)
