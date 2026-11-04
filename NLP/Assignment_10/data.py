from __future__ import annotations

import csv
import re
from pathlib import Path
from collections import Counter
from typing import Iterable

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

TOKEN_RE = re.compile(r"[a-z]+")


def preprocess(text: object) -> list[str]:
    tokens = TOKEN_RE.findall(str(text).lower())
    return [token for token in tokens if token not in ENGLISH_STOP_WORDS]


def _read_rows(path: Path) -> Iterable[tuple[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = csv.reader(handle)
        first = next(rows, None)
        if first is None:
            return
        lowered = {value.strip().lower() for value in first}
        has_header = bool({"review", "text", "content"} & lowered)
        if not has_header:
            yield first[0], first[-1]
        for row in rows:
            if len(row) >= 2:
                yield row[0], row[-1]


def _quotas(counts: Counter[str], sample_size: int) -> dict[str, int]:
    total = sum(counts.values())
    raw = {label: sample_size * count / total for label, count in counts.items()}
    quotas = {label: int(value) for label, value in raw.items()}
    remaining = sample_size - sum(quotas.values())
    for label, _ in sorted(
        raw.items(), key=lambda item: item[1] - quotas[item[0]], reverse=True
    )[:remaining]:
        quotas[label] += 1
    return quotas


def _stratified_file(
    path: Path, sample_size: int, random_state: int
) -> tuple[list[list[str]], list[str]]:
    counts = Counter(label for label, _ in _read_rows(path))
    quotas = _quotas(counts, sample_size)
    reservoirs: dict[str, list[str]] = {label: [] for label in quotas}
    seen = Counter()
    rng = __import__("random").Random(random_state)
    for label, review in _read_rows(path):
        if label not in quotas:
            continue
        seen[label] += 1
        bucket = reservoirs[label]
        if len(bucket) < quotas[label]:
            bucket.append(review)
        else:
            index = rng.randrange(seen[label])
            if index < quotas[label]:
                bucket[index] = review
    reviews = [review for bucket in reservoirs.values() for review in bucket]
    labels = [
        label for label, bucket in reservoirs.items() for _ in bucket
    ]
    order = list(range(len(reviews)))
    rng.shuffle(order)
    return [preprocess(reviews[index]) for index in order], [
        labels[index] for index in order
    ]


def load_stratified_data(
    train_path: Path,
    test_path: Path,
    train_size: int = 10_000,
    test_size: int = 1_000,
    random_state: int = 42,
) -> tuple[list[list[str]], list[str], list[list[str]], list[str]]:
    train_tokens, train_labels = _stratified_file(
        train_path, train_size, random_state
    )
    test_tokens, test_labels = _stratified_file(
        test_path, test_size, random_state + 1
    )
    return (
        train_tokens,
        train_labels,
        test_tokens,
        test_labels,
    )


def vocabulary(sentences: Iterable[list[str]]) -> set[str]:
    return {token for sentence in sentences for token in sentence}
