import hashlib
import math
import re
from typing import Protocol


class EmbeddingProvider(Protocol):
    def embed_query(self, text: str) -> list[float]:
        raise NotImplementedError

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class HashingEmbeddingProvider:
    def __init__(self, dimensions: int = 256) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be greater than 0.")

        self.dimensions = dimensions

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions

        for token in re.findall(r"[A-Za-z0-9]+", text.lower()):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector

        return [value / norm for value in vector]
