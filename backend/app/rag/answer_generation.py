from app.rag.models import GeneratedAnswer, SearchResult, SourceCitation


class SourceCitedAnswerGenerator:
    def generate(self, question: str, results: list[SearchResult]) -> GeneratedAnswer:
        if not results:
            return GeneratedAnswer(
                answer="I do not have enough retrieved context to answer that question.",
                citations=[],
            )

        citations: list[SourceCitation] = []
        context_points: list[str] = []
        seen_contexts: set[str] = set()

        for result in results:
            chunk = result.chunk
            excerpt = " ".join(chunk.text.split())
            normalized_excerpt = excerpt.casefold()
            if normalized_excerpt in seen_contexts:
                continue

            source_id = len(citations) + 1
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
            seen_contexts.add(normalized_excerpt)
            context_points.append(f"{excerpt} [{source_id}]")

        answer = " ".join(context_points)
        return GeneratedAnswer(answer=answer, citations=citations)
