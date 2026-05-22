from app.rag.models import GeneratedAnswer, SearchResult, SourceCitation


class SourceCitedAnswerGenerator:
    def generate(self, question: str, results: list[SearchResult]) -> GeneratedAnswer:
        if not results:
            return GeneratedAnswer(
                answer="I do not have enough retrieved context to answer that question.",
                citations=[],
            )

        cited_lines = []
        citations: list[SourceCitation] = []

        for source_id, result in enumerate(results, start=1):
            chunk = result.chunk
            citations.append(
                SourceCitation(
                    source_id=source_id,
                    document_id=chunk.document_id,
                    filename=chunk.filename,
                    chunk_index=chunk.chunk_index,
                    start_char=chunk.start_char,
                    end_char=chunk.end_char,
                )
            )
            excerpt = " ".join(chunk.text.split())
            cited_lines.append(f"[{source_id}] {excerpt}")

        answer = (
            f"Based on the retrieved document context for: {question}\n\n"
            + "\n\n".join(cited_lines)
        )
        return GeneratedAnswer(answer=answer, citations=citations)
