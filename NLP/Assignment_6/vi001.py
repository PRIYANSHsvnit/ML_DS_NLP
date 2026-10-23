from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


def load_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def plot_perplexity(rows, out_path):
    # Exclude Stupid Backoff from "standard PPL" comparison in the title.
    filtered = [
        r for r in rows
        if r["method"] != "stupid_backoff"
    ]

    labels = [r["label"] for r in filtered]
    values = [float(r["perplexity"]) for r in filtered]

    fig_width = max(12, len(labels) * 0.75)
    plt.figure(figsize=(fig_width, 6))
    plt.bar(range(len(values)), values)
    plt.xticks(
        range(len(values)),
        labels,
        rotation=60,
        ha="right",
    )
    plt.ylabel("Perplexity (lower is better)")
    plt.title("N-gram Smoothing Comparison")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def plot_by_order(rows, out_path):
    methods = sorted({
        r["method"]
        for r in rows
        if r["method"] != "stupid_backoff"
    })

    orders = [2, 3, 4]

    plt.figure(figsize=(10, 6))

    for method in methods:
        points = []

        for order in orders:
            matched = [
                r for r in rows
                if r["method"] == method
                and int(r["order"]) == order
            ]

            if matched:
                points.append(float(matched[0]["perplexity"]))
            else:
                points.append(float("nan"))

        plt.plot(
            orders,
            points,
            marker="o",
            label=method.replace("_", " ").title(),
        )

    plt.xticks(orders, ["Bigram", "Trigram", "Quadgram"])
    plt.xlabel("Model Order")
    plt.ylabel("Perplexity (lower is better)")
    plt.title("Effect of Model Order on Smoothing Performance")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def print_table(rows):
    rows = sorted(
        rows,
        key=lambda r: (
            int(r["order"]),
            float(r["perplexity"]),
        )
    )

    print(
        f"{'Model':35} "
        f"{'Order':>5} "
        f"{'PPL':>12} "
        f"{'Zero events':>14} "
        f"{'Tok/s':>12}"
    )
    print("-" * 85)

    for r in rows:
        print(
            f"{r['label']:35} "
            f"{r['order']:>5} "
            f"{float(r['perplexity']):>12.4f} "
            f"{int(float(r['zero_probability_events'])):>14,} "
            f"{float(r['tokens_per_second']):>12.1f}"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--csv",
        default="results/test_results.csv",
    )
    parser.add_argument(
        "--out-dir",
        default="results/plots",
    )
    args = parser.parse_args()

    rows = load_csv(args.csv)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    print_table(rows)

    plot_perplexity(
        rows,
        out / "test_perplexity_comparison.png",
    )

    plot_by_order(
        rows,
        out / "test_perplexity_by_order.png",
    )

    print(f"\nPlots saved to: {out.resolve()}")


if __name__ == "__main__":
    main()
