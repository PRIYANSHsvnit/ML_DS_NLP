from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def write_metrics(
    output_dir: Path,
    split: str,
    scores: dict[str, dict[str, float]],
    token_count: int,
    plots: bool,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tags = sorted(
        tag for values in scores.values() for tag in values if tag != "__overall__"
    )
    tags = sorted(set(tags))
    with (output_dir / f"{split}_metrics.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(["tag", *scores])
        for tag in tags:
            writer.writerow([tag, *(f"{scores[name][tag]:.6f}" for name in scores)])
        writer.writerow(
            ["__overall_accuracy__", *(f"{scores[name]['__overall__']:.6f}" for name in scores)]
        )
    if not plots:
        return
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed; CSV results were written.")
        return
    figure, axis = plt.subplots(figsize=(max(12, len(tags) * 0.35), 6))
    positions = list(range(len(tags)))
    width = 0.8 / len(scores)
    for offset, (name, values) in enumerate(scores.items()):
        axis.bar(
            [position + offset * width for position in positions],
            [values[tag] for tag in tags],
            width=width,
            label=name,
        )
    axis.set_xticks([p + width * (len(scores) - 1) / 2 for p in positions])
    axis.set_xticklabels(tags, rotation=75, ha="right")
    axis.set_ylim(0, 1)
    axis.set_ylabel("F1-score")
    axis.set_title(f"Hindi POS tagging - {split} per-tag F1")
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_dir / f"{split}_per_tag_f1.png", dpi=150)
    plt.close(figure)


def write_results(output_dir: Path, payload: dict[str, Any]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "results.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
