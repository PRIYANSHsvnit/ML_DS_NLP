from __future__ import annotations

import argparse
import csv
from pathlib import Path


def show_results(results_dir: Path) -> None:
    for split in ("dev", "test"):
        path = results_dir / f"{split}_f1.csv"
        if not path.exists():
            print(f"{split}: no result file at {path}")
            continue
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        summary = rows[-1]
        models = [key for key in summary if key != "tag"]
        ranked = sorted(
            ((model, float(summary[model])) for model in models),
            key=lambda item: item[1],
            reverse=True,
        )
        print(f"\n{split.upper()} RESULTS")
        for model, score in ranked:
            print(f"  {model:22} {score:.4f}")
        print(f"  Per-tag F1 rows: {len(rows) - 1}")
        print(f"  Chart: {results_dir / f'{split}_f1.png'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="View Assignment 7 result summaries.")
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    show_results(parser.parse_args().results_dir)
