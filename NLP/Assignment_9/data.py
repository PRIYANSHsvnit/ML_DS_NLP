from __future__ import annotations

from pathlib import Path
from typing import Iterable, Iterator

Sentence = list[tuple[str, str]]


def read_sentences(path: Path) -> Iterator[Sentence]:
    sentence: Sentence = []
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                if sentence:
                    yield sentence
                    sentence = []
                continue
            fields = line.split()
            if len(fields) != 2:
                raise ValueError(f"Expected WORD TAG, got {line!r} in {path}")
            sentence.append((fields[0], fields[1]))
    if sentence:
        yield sentence


def limit_sentences(
    sentences: Iterable[Sentence],
    max_sentences: int | None = None,
    max_tokens: int | None = None,
) -> Iterator[Sentence]:
    token_count = 0
    for index, sentence in enumerate(sentences):
        if max_sentences is not None and index >= max_sentences:
            break
        if max_tokens is not None and token_count >= max_tokens:
            break
        if max_tokens is not None:
            sentence = sentence[: max_tokens - token_count]
        if sentence:
            yield sentence
            token_count += len(sentence)
