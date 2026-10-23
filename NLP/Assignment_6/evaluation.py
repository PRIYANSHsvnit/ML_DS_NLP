from __future__ import annotations

import argparse
import csv
import math
import time
from pathlib import Path

from data_loader import UNK, iter_sentences
from ngram_model import CountStore, sentence_probability


def parse_lambda(text: str):
    values = [float(x.strip()) for x in text.split(",") if x.strip()]
    if not values:
        raise ValueError("Lambda list cannot be empty.")
    total = sum(values)
    if total <= 0:
        raise ValueError("Lambda sum must be positive.")
    # Normalise automatically, while still allowing the user to pass
    # approximate weights.
    return [x / total for x in values]


def evaluate_model(
    store: CountStore,
    file_path: str,
    method: str,
    order: int,
    max_sentences: int | None = None,
    **kwargs,
):
    start = time.perf_counter()

    total_logp = 0.0
    total_tokens = 0
    total_zeros = 0
    sentences = 0

    for tokens in iter_sentences(
        file_path,
        add_boundaries=True,
        max_order=4,
    ):
        # Training counts use three BOS markers so the same SQLite database
        # supports orders 2, 3, and 4. Remove only the excess BOS markers for
        # this evaluation order, retaining exactly order-1 context markers.
        if order < 4:
            tokens = tokens[4 - order:]

        # At evaluation time, unknown test/dev words should become <UNK>.
        # The vocabulary contains exactly the training vocabulary.
        vocabulary = None
        # We avoid loading the full vocabulary repeatedly. CountStore has
        # a cached unigram lookup; unknown words simply have count 0.
        # Replace unknown tokens directly using get_unigram_count.
        tokens = [
            t if store.get_unigram_count(t) > 0 else UNK
            for t in tokens
        ]

        # A lower-order model inside a higher-order evaluation still starts
        # from the requested maximum order.
        logp, n, z = sentence_probability(
            store,
            tokens,
            method,
            order,
            **kwargs,
        )

        total_logp += logp
        total_tokens += n
        total_zeros += z
        sentences += 1

        if max_sentences and sentences >= max_sentences:
            break

    elapsed = time.perf_counter() - start

    # Natural-log cross entropy.
    cross_entropy_nats = (
        -total_logp / total_tokens
        if total_tokens else float("inf")
    )

    # Perplexity in the mathematical sense is meaningful for the
    # normalized methods only.
    perplexity = (
        math.exp(cross_entropy_nats)
        if total_tokens
        else float("inf")
    )

    reported_perplexity = perplexity

    if method == "mle" and total_zeros > 0:
        reported_perplexity = float("inf")

    result = {
        "method": method,
        "order": order,
        "file": str(file_path),
        "sentences": sentences,
        "tokens": total_tokens,
        "zero_probability_events": total_zeros,
        "cross_entropy_nats": cross_entropy_nats,
        "perplexity": reported_perplexity,
        "seconds": elapsed,
        "tokens_per_second": (
            total_tokens / elapsed if elapsed > 0 else 0.0
        ),
    }

    # For Stupid Backoff this must not be interpreted as true
    # normalized-model perplexity.
    if method == "stupid_backoff":
        result["perplexity_note"] = (
            "pseudo-PPL only; SB scores are not normalized probabilities"
        )
    else:
        result["perplexity_note"] = "standard PPL"

    return result


def make_experiments():
    """
    Default experiments.

    These are sensible starting values, not claims that they are optimal.
    For the report, select/tune them on the development set.
    """
    return [
        # Baseline
        {
            "method": "mle",
            "order": 2,
            "kwargs": {},
            "label": "Bigram-MLE",
        },
        {
            "method": "mle",
            "order": 3,
            "kwargs": {},
            "label": "Trigram-MLE",
        },
        {
            "method": "mle",
            "order": 4,
            "kwargs": {},
            "label": "Quadgram-MLE",
        },

        # Bigram
        {
            "method": "interpolation",
            "order": 2,
            "kwargs": {"lambdas": [0.20, 0.80]},
            "label": "Bigram-Interpolation",
        },
        {
            "method": "good_turing",
            "order": 2,
            "kwargs": {"cutoff": 5},
            "label": "Bigram-GoodTuring",
        },
        {
            "method": "katz",
            "order": 2,
            "kwargs": {"cutoff": 5},
            "label": "Bigram-Katz",
        },
        {
            "method": "stupid_backoff",
            "order": 2,
            "kwargs": {"alpha": 0.40},
            "label": "Bigram-StupidBackoff",
        },
        {
            "method": "kneser_ney",
            "order": 2,
            "kwargs": {"D": 0.75},
            "label": "Bigram-KneserNey",
        },

        # Trigram
        {
            "method": "interpolation",
            "order": 3,
            "kwargs": {"lambdas": [0.10, 0.25, 0.65]},
            "label": "Trigram-Interpolation",
        },
        {
            "method": "good_turing",
            "order": 3,
            "kwargs": {"cutoff": 5},
            "label": "Trigram-GoodTuring",
        },
        {
            "method": "katz",
            "order": 3,
            "kwargs": {"cutoff": 5},
            "label": "Trigram-Katz",
        },
        {
            "method": "stupid_backoff",
            "order": 3,
            "kwargs": {"alpha": 0.40},
            "label": "Trigram-StupidBackoff",
        },
        {
            "method": "kneser_ney",
            "order": 3,
            "kwargs": {"D": 0.75},
            "label": "Trigram-KneserNey",
        },

        # Quadgram
        {
            "method": "interpolation",
            "order": 4,
            "kwargs": {"lambdas": [0.05, 0.15, 0.25, 0.55]},
            "label": "Quadgram-Interpolation",
        },
        {
            "method": "good_turing",
            "order": 4,
            "kwargs": {"cutoff": 5},
            "label": "Quadgram-GoodTuring",
        },
        {
            "method": "katz",
            "order": 4,
            "kwargs": {"cutoff": 5},
            "label": "Quadgram-Katz",
        },
        {
            "method": "stupid_backoff",
            "order": 4,
            "kwargs": {"alpha": 0.40},
            "label": "Quadgram-StupidBackoff",
        },
        {
            "method": "kneser_ney",
            "order": 4,
            "kwargs": {"D": 0.75},
            "label": "Quadgram-KneserNey",
        },
    ]


def run_suite(
    db_path: str,
    eval_file: str,
    output_csv: str,
    max_sentences: int | None = None,
):
    rows = []

    with CountStore(db_path) as store:
        for exp in make_experiments():
            print(
                f"[EVAL] {exp['label']} on "
                f"{Path(eval_file).name} ..."
            )

            result = evaluate_model(
                store,
                eval_file,
                exp["method"],
                exp["order"],
                max_sentences=max_sentences,
                **exp["kwargs"],
            )
            result["label"] = exp["label"]
            result.update(exp["kwargs"])
            rows.append(result)

            print(
                f"    PPL={result['perplexity']:.4f} | "
                f"zeros={result['zero_probability_events']:,} | "
                f"time={result['seconds']:.2f}s"
            )

    output_csv = Path(output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = sorted({
        key
        for row in rows
        for key in row.keys()
    })

    with output_csv.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[EVAL] Saved: {output_csv.resolve()}")


def tune_interpolation_on_dev(
    db_path: str,
    dev_file: str,
    order: int,
    step: float = 0.10,
    max_sentences: int | None = None,
):
    """
    Simple grid search over interpolation weights.

    The weights are generated recursively and constrained to sum to 1.
    This is intended for the development set only.
    """
    with CountStore(db_path) as store:
        best = None

        def compositions(n, remaining, prefix):
            if n == 1:
                yield prefix + [remaining]
                return

            x = 0.0
            while x <= remaining + 1e-9:
                yield from compositions(
                    n - 1,
                    round(remaining - x, 10),
                    prefix + [round(x, 10)]
                )
                x += step

        for lambdas in compositions(order, 1.0, []):
            result = evaluate_model(
                store,
                dev_file,
                "interpolation",
                order,
                max_sentences=max_sentences,
                lambdas=lambdas,
            )

            if best is None or result["perplexity"] < best["perplexity"]:
                best = {
                    "lambdas": lambdas,
                    "perplexity": result["perplexity"],
                }

        return best


def tune_simple_parameter(
    db_path: str,
    dev_file: str,
    method: str,
    order: int,
    values,
    parameter_name: str,
    max_sentences: int | None = None,
):
    """
    Tune one scalar smoothing parameter on the dev set.

    Examples:
        method='kneser_ney', parameter_name='D'
        method='stupid_backoff', parameter_name='alpha'
        method='good_turing', parameter_name='cutoff'
    """
    best = None

    with CountStore(db_path) as store:
        for value in values:
            result = evaluate_model(
                store,
                dev_file,
                method,
                order,
                max_sentences=max_sentences,
                **{parameter_name: value},
            )

            if best is None or result["perplexity"] < best["perplexity"]:
                best = {
                    "value": value,
                    "parameter": parameter_name,
                    "perplexity": result["perplexity"],
                }

            print(
                f"{method} order={order} "
                f"{parameter_name}={value} "
                f"PPL={result['perplexity']:.4f}"
            )

    return best


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate all smoothing techniques."
    )
    parser.add_argument("--db", default="ngram_model.db")
    parser.add_argument("--dev", default="splits/dev.txt")
    parser.add_argument("--test", default="splits/test.txt")
    parser.add_argument(
        "--out-dir",
        default="results",
    )
    parser.add_argument(
        "--max-sentences",
        type=int,
        default=None,
        help="Useful for a fast sanity test. Omit for full evaluation.",
    )
    args = parser.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    print("\n========== DEVELOPMENT SET ==========\n")
    run_suite(
        args.db,
        args.dev,
        out / "development_results.csv",
        max_sentences=args.max_sentences,
    )

    print("\n========== TEST SET ==========\n")
    run_suite(
        args.db,
        args.test,
        out / "test_results.csv",
        max_sentences=args.max_sentences,
    )


if __name__ == "__main__":
    main()
