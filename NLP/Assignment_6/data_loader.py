from __future__ import annotations

from pathlib import Path
import random
from collections import Counter
from typing import Iterator, List, Tuple


BOS = "<s>"
EOS = "</s>"
UNK = "<UNK>"


def iter_sentences(path: str | Path,
                   add_boundaries: bool = True,
                   max_order: int = 4) -> Iterator[List[str]]:
    """
    Stream a tokenized text file one line at a time.

    Expected format:
        one tokenized sentence per line
        tokens separated by whitespace

    Example:
        यह एक उदाहरण है
    """
    path = Path(path)

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            tokens = line.split()

            if add_boundaries:
                # For an N-gram model of order N, prepend N-1 BOS tokens.
                tokens = [BOS] * (max_order - 1) + tokens + [EOS]

            yield tokens


def count_nonempty_lines(path: str | Path) -> int:
    path = Path(path)
    count = 0

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.strip():
                count += 1

    return count


def split_file(
    input_path: str | Path,
    train_path: str | Path,
    dev_path: str | Path,
    test_path: str | Path,
    train_ratio: float = 0.80,
    dev_ratio: float = 0.10,
    seed: int = 42,
) -> Tuple[int, int, int]:
    """
    Deterministically split a large line-oriented corpus.

    The split is randomised with a fixed seed but is streamed, so the
    complete 1M-row corpus is never loaded into RAM.
    """
    if not (0.0 < train_ratio < 1.0):
        raise ValueError("train_ratio must be between 0 and 1.")
    if not (0.0 <= dev_ratio < 1.0):
        raise ValueError("dev_ratio must be between 0 and 1.")
    if train_ratio + dev_ratio >= 1.0:
        raise ValueError("train_ratio + dev_ratio must be < 1.")

    input_path = Path(input_path)
    train_path = Path(train_path)
    dev_path = Path(dev_path)
    test_path = Path(test_path)

    for p in (train_path, dev_path, test_path):
        p.parent.mkdir(parents=True, exist_ok=True)

    rng = random.Random(seed)

    counts = {"train": 0, "dev": 0, "test": 0}

    with (
        input_path.open("r", encoding="utf-8", errors="ignore") as src,
        train_path.open("w", encoding="utf-8") as train,
        dev_path.open("w", encoding="utf-8") as dev,
        test_path.open("w", encoding="utf-8") as test,
    ):
        for line in src:
            if not line.strip():
                continue

            r = rng.random()

            if r < train_ratio:
                train.write(line)
                counts["train"] += 1
            elif r < train_ratio + dev_ratio:
                dev.write(line)
                counts["dev"] += 1
            else:
                test.write(line)
                counts["test"] += 1

    return counts["train"], counts["dev"], counts["test"]


def prepare_sentence_tokens(
    tokens: List[str],
    vocabulary: set[str] | None = None,
    max_order: int = 4,
) -> List[str]:
    """
    Convert tokens to the exact representation used by the model.
    If a vocabulary is supplied, unseen tokens are mapped to <UNK>.
    """
    if vocabulary is not None:
        tokens = [t if t in vocabulary else UNK for t in tokens]

    return [BOS] * (max_order - 1) + tokens + [EOS]


def build_vocabulary_from_file(
    path: str | Path,
    min_count: int = 1,
) -> tuple[set[str], Counter]:
    """
    First pass over the training file.

    Words with raw training frequency <= min_count are mapped to <UNK>
    during the second n-gram counting pass. Keeping the vocabulary bounded
    prevents OOV test/dev words from receiving a zero unigram probability.
    """
    path = Path(path)
    raw_counts = Counter()

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if not line.strip():
                continue
            raw_counts.update(line.strip().split())

    vocabulary = {
        word
        for word, count in raw_counts.items()
        if count > min_count
    }

    vocabulary.update({BOS, EOS, UNK})
    return vocabulary, raw_counts
