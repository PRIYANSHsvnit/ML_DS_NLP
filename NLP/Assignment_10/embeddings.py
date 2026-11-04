from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np


class EmbeddingStore:
    """Small lookup interface shared by binary and text vector formats."""

    dimension: int

    def contains(self, word: str) -> bool:
        raise NotImplementedError

    def vector(self, word: str) -> np.ndarray | None:
        raise NotImplementedError

    def nearest_analogy(self, a: str, b: str, c: str) -> str | None:
        raise NotImplementedError

    def close(self) -> None:
        pass


class GensimEmbeddingStore(EmbeddingStore):
    def __init__(
        self, path: Path, binary: bool, no_header: bool = False, native: bool = False
    ) -> None:
        from gensim.models import KeyedVectors

        if native:
            sidecar = Path(f"{path}.vectors.npy")
            if not sidecar.exists():
                raise FileNotFoundError(
                    "The Gensim Word2Vec file is incomplete. "
                    f"Missing sidecar: {sidecar}. "
                    "Download the complete model bundle, or replace this "
                    "file with a standalone GoogleNews-vectors-negative300.bin."
                )
            self._vectors = KeyedVectors.load(str(path), mmap="r")
        else:
            self._vectors = KeyedVectors.load_word2vec_format(
                str(path), binary=binary, no_header=no_header
            )
        self.dimension = self._vectors.vector_size

    def contains(self, word: str) -> bool:
        return word in self._vectors.key_to_index

    def vector(self, word: str) -> np.ndarray | None:
        if not self.contains(word):
            return None
        return np.asarray(self._vectors[word], dtype=np.float32)

    def nearest_analogy(self, a: str, b: str, c: str) -> str | None:
        matches = self._vectors.most_similar(
            positive=[b, c], negative=[a], topn=1
        )
        return matches[0][0] if matches else None

    def close(self) -> None:
        del self._vectors


def load_embedding(
    path: Path, words: Iterable[str], format_name: str
) -> EmbeddingStore:
    if not path.exists():
        raise FileNotFoundError(f"Embedding file does not exist: {path}")
    if format_name == "word2vec-bin":
        return GensimEmbeddingStore(path, binary=True)
    if format_name == "word2vec-native":
        return GensimEmbeddingStore(path, binary=False, native=True)
    if format_name == "glove-text":
        return GensimEmbeddingStore(path, binary=False, no_header=True)
    if format_name in {"word2vec-text", "fasttext-text"}:
        return GensimEmbeddingStore(path, binary=False)
    raise ValueError(f"Unsupported embedding format: {format_name}")
