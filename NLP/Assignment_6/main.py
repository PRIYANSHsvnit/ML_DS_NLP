from __future__ import annotations

import argparse
from pathlib import Path

from data_loader import (
    iter_sentences,
    split_file,
    build_vocabulary_from_file,
)
from ngram_model import CountStore


def parse_args():
    p = argparse.ArgumentParser(
        description="Build a SQLite-backed 1-4 gram language model."
    )

    p.add_argument(
        "--data",
        default="indic_tokenized.txt",
        help="Path to the tokenized corpus.",
    )
    p.add_argument(
        "--db",
        default="ngram_model.db",
        help="SQLite database path.",
    )
    p.add_argument(
        "--splits-dir",
        default="splits",
        help="Directory for train/dev/test files.",
    )
    p.add_argument(
        "--train-ratio",
        type=float,
        default=0.80,
    )
    p.add_argument(
        "--dev-ratio",
        type=float,
        default=0.10,
    )
    p.add_argument(
        "--seed",
        type=int,
        default=42,
    )
    p.add_argument(
        "--rebuild-split",
        action="store_true",
        help="Recreate train/dev/test files.",
    )
    p.add_argument(
        "--rebuild-db",
        action="store_true",
        help="Delete counts and rebuild the SQLite database.",
    )
    p.add_argument(
        "--commit-every",
        type=int,
        default=10000,
    )

    return p.parse_args()


def main():
    args = parse_args()

    data = Path(args.data)
    if not data.exists():
        raise FileNotFoundError(
            f"Corpus not found: {data.resolve()}"
        )

    splits = Path(args.splits_dir)
    splits.mkdir(parents=True, exist_ok=True)

    train_file = splits / "train.txt"
    dev_file = splits / "dev.txt"
    test_file = splits / "test.txt"

    if (
        args.rebuild_split
        or not train_file.exists()
        or not dev_file.exists()
        or not test_file.exists()
    ):
        print("[1/3] Splitting corpus...")
        train_n, dev_n, test_n = split_file(
            data,
            train_file,
            dev_file,
            test_file,
            train_ratio=args.train_ratio,
            dev_ratio=args.dev_ratio,
            seed=args.seed,
        )
        print(
            f"train={train_n:,} | "
            f"dev={dev_n:,} | "
            f"test={test_n:,}"
        )
    else:
        print("[1/3] Existing train/dev/test split found.")

    print("[2/3] Building n-gram SQLite database...")
    with CountStore(args.db) as store:
        # Empty DB or explicit rebuild.
        is_empty = store.get_meta("num_sentences") is None

        if args.rebuild_db or is_empty:
            print("[VOCAB] First pass: building training vocabulary...")

            vocabulary, raw_counts = build_vocabulary_from_file(
                train_file,
                min_count=1,
            )

            rare_token_count = sum(
                c for word, c in raw_counts.items()
                if c <= 1
            )

            print(
                f"[VOCAB] raw types={len(raw_counts):,} | "
                f"model vocab={len(vocabulary):,} | "
                f"tokens mapped to <UNK>={rare_token_count:,}"
            )

            print("[BUILD] Second pass: building mapped n-gram counts...")

            store.build_from_sentences(
                (
                    tokens
                    for tokens in iter_sentences(
                        train_file,
                        add_boundaries=True,
                        max_order=4,
                    )
                ),
                commit_every=args.commit_every,
                reset=args.rebuild_db,
                vocabulary=vocabulary,
                unk_cutoff=1,
            )
            store.set_meta("unk_cutoff", 1)
        else:
            print(
                "Existing ngram_model.db detected. "
                "Use --rebuild-db to rebuild."
            )

        print("[3/3] Model information")
        print(f"Database: {Path(args.db).resolve()}")
        print(f"Sentences: {store.get_meta('num_sentences')}")
        print(f"Tokens: {store.get_meta('total_tokens')}")
        print(f"Vocabulary: {store.get_meta('vocab_size')}")


if __name__ == "__main__":
    main()
