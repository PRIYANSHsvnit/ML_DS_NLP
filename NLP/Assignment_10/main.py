from __future__ import annotations

import argparse
from pathlib import Path

from runner import run


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resource-aware Assignment 10 embedding comparison."
    )
    root = Path(__file__).parent
    parser.add_argument(
        "--train",
        type=Path,
        default=root / "data" / "amazon" / "train.csv",
        help="train.csv path",
    )
    parser.add_argument(
        "--test",
        type=Path,
        default=root / "data" / "amazon" / "test.csv",
        help="test.csv path",
    )
    parser.add_argument(
        "--analogy",
        type=Path,
        default=root / "data" / "analogies" / "questions-words.txt",
        help="questions-words.txt path",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--train-size", type=int, default=10_000)
    parser.add_argument("--test-size", type=int, default=1_000)
    parser.add_argument(
        "--max-analogies",
        type=int,
        default=None,
        help="Optional cap for a quick run; default evaluates all analogy rows.",
    )
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument(
        "--embeddings",
        nargs="+",
        choices=("word2vec", "glove", "fasttext"),
        default=("word2vec", "glove", "fasttext"),
        help="Embedding models to run; default runs all three.",
    )
    parser.add_argument(
        "--word2vec",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--glove",
        type=Path,
        default=root / "data" / "embeddings" / "glove.6B.300d.txt",
    )
    parser.add_argument(
        "--fasttext",
        type=Path,
        default=root / "data" / "embeddings" / "wiki-news-300d-1M-subword.vec",
    )
    args = parser.parse_args()
    if args.word2vec is None:
        model_path = root / "data" / "embeddings" / "word2vec-google-news-300.model"
        binary_path = root / "data" / "embeddings" / "GoogleNews-vectors-negative300.bin"
        args.word2vec = model_path if model_path.exists() else binary_path
    embeddings = {}
    if "word2vec" in args.embeddings:
        word2vec_format = (
            "word2vec-native"
            if args.word2vec.suffix.lower() == ".model"
            else "word2vec-bin"
        )
        embeddings["word2vec"] = (args.word2vec, word2vec_format)
    if "glove" in args.embeddings:
        embeddings["glove"] = (args.glove, "glove-text")
    if "fasttext" in args.embeddings:
        embeddings["fasttext"] = (args.fasttext, "fasttext-text")
    result = run(
        args.train,
        args.test,
        args.output_dir,
        embeddings,
        args.analogy,
        args.train_size,
        args.test_size,
        args.max_analogies,
        args.random_state,
    )
    print(f"[complete] results written to {result.resolve()}")


if __name__ == "__main__":
    main()
