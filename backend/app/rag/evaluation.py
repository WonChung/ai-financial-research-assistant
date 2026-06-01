from dataclasses import asdict, dataclass
from time import perf_counter

from app.rag.models import SourceCitation
from app.rag.pipeline import RagService


@dataclass(frozen=True)
class EvaluationCase:
    document_id: str
    question: str
    expected_answer_phrases: list[str]
    expected_citation_phrases: list[str]
    top_k: int = 5
    case_id: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class EvaluationCheck:
    name: str
    passed: bool
    failure_reason: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class EvaluationResult:
    case: EvaluationCase
    answer: str
    citations: list[SourceCitation]
    cited_source_count: int
    latency_ms: float
    checks: list[EvaluationCheck]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    def to_dict(self) -> dict[str, object]:
        return {
            "case": self.case.to_dict(),
            "answer": self.answer,
            "citations": [asdict(citation) for citation in self.citations],
            "cited_source_count": self.cited_source_count,
            "latency_ms": self.latency_ms,
            "checks": [check.to_dict() for check in self.checks],
            "passed": self.passed,
        }


@dataclass(frozen=True)
class EvaluationSummary:
    results: list[EvaluationResult]

    @property
    def total_cases(self) -> int:
        return len(self.results)

    @property
    def passed_cases(self) -> int:
        return sum(1 for result in self.results if result.passed)

    @property
    def failed_cases(self) -> int:
        return self.total_cases - self.passed_cases

    @property
    def pass_rate(self) -> float:
        if self.total_cases == 0:
            return 0.0
        return self.passed_cases / self.total_cases

    @property
    def average_latency_ms(self) -> float:
        if self.total_cases == 0:
            return 0.0
        return sum(result.latency_ms for result in self.results) / self.total_cases

    def to_dict(self) -> dict[str, object]:
        return {
            "total_cases": self.total_cases,
            "passed_cases": self.passed_cases,
            "failed_cases": self.failed_cases,
            "pass_rate": self.pass_rate,
            "average_latency_ms": self.average_latency_ms,
            "results": [result.to_dict() for result in self.results],
        }


class RagEvaluator:
    def __init__(self, rag_service: RagService) -> None:
        self.rag_service = rag_service

    def evaluate_case(self, case: EvaluationCase) -> EvaluationResult:
        start_time = perf_counter()
        generated_answer = self.rag_service.answer(
            document_id=case.document_id,
            question=case.question,
            top_k=case.top_k,
        )
        latency_ms = (perf_counter() - start_time) * 1000

        cited_context = self._cited_context(
            document_id=case.document_id,
            question=case.question,
            top_k=case.top_k,
            citations=generated_answer.citations,
        )
        checks = [
            self._retrieval_check(generated_answer.citations),
            self._answer_phrase_check(
                generated_answer.answer,
                case.expected_answer_phrases,
            ),
            self._citation_phrase_check(cited_context, case.expected_citation_phrases),
            self._answer_grounding_check(
                generated_answer.answer,
                generated_answer.citations,
            ),
        ]

        return EvaluationResult(
            case=case,
            answer=generated_answer.answer,
            citations=generated_answer.citations,
            cited_source_count=len(generated_answer.citations),
            latency_ms=latency_ms,
            checks=checks,
        )

    def evaluate(self, cases: list[EvaluationCase]) -> EvaluationSummary:
        return EvaluationSummary(
            results=[self.evaluate_case(case) for case in cases],
        )

    def _cited_context(
        self,
        *,
        document_id: str,
        question: str,
        top_k: int,
        citations: list[SourceCitation],
    ) -> str:
        if not citations:
            return ""

        citation_keys = {
            (citation.document_id, citation.chunk_index) for citation in citations
        }
        retrieved_results = self.rag_service.retriever.retrieve(
            document_id=document_id,
            query=question,
            top_k=top_k,
        )
        cited_texts = [
            result.chunk.text
            for result in retrieved_results
            if (result.chunk.document_id, result.chunk.chunk_index) in citation_keys
        ]
        return " ".join(cited_texts)

    @staticmethod
    def _retrieval_check(citations: list[SourceCitation]) -> EvaluationCheck:
        if citations:
            return EvaluationCheck(name="retrieval_has_citations", passed=True)
        return EvaluationCheck(
            name="retrieval_has_citations",
            passed=False,
            failure_reason="Expected at least one cited source, but none were returned.",
        )

    @staticmethod
    def _answer_phrase_check(
        answer: str,
        expected_phrases: list[str],
    ) -> EvaluationCheck:
        missing_phrases = missing_expected_phrases(answer, expected_phrases)
        if not missing_phrases:
            return EvaluationCheck(name="expected_answer_phrases", passed=True)
        return EvaluationCheck(
            name="expected_answer_phrases",
            passed=False,
            failure_reason=(
                "Missing expected answer phrase(s): "
                + ", ".join(repr(phrase) for phrase in missing_phrases)
            ),
        )

    @staticmethod
    def _citation_phrase_check(
        cited_context: str,
        expected_phrases: list[str],
    ) -> EvaluationCheck:
        missing_phrases = missing_expected_phrases(cited_context, expected_phrases)
        if not missing_phrases:
            return EvaluationCheck(name="expected_citation_phrases", passed=True)
        return EvaluationCheck(
            name="expected_citation_phrases",
            passed=False,
            failure_reason=(
                "Missing expected cited context phrase(s): "
                + ", ".join(repr(phrase) for phrase in missing_phrases)
            ),
        )

    @staticmethod
    def _answer_grounding_check(
        answer: str,
        citations: list[SourceCitation],
    ) -> EvaluationCheck:
        missing_markers = [
            f"[{citation.source_id}]"
            for citation in citations
            if f"[{citation.source_id}]" not in answer
        ]
        if not missing_markers:
            return EvaluationCheck(name="answer_citation_markers", passed=True)
        return EvaluationCheck(
            name="answer_citation_markers",
            passed=False,
            failure_reason=(
                "Answer is missing citation marker(s): " + ", ".join(missing_markers)
            ),
        )


def missing_expected_phrases(text: str, expected_phrases: list[str]) -> list[str]:
    normalized_text = normalize_for_phrase_match(text)
    return [
        phrase
        for phrase in expected_phrases
        if normalize_for_phrase_match(phrase) not in normalized_text
    ]


def normalize_for_phrase_match(text: str) -> str:
    return " ".join(text.split()).casefold()
