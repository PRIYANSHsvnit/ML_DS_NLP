from __future__ import annotations

import csv
from pathlib import Path


def write_report(output_dir: Path, split: str, scores: dict[str, dict[str, float]], plots: bool = True) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tags = sorted(tag for tag in next(iter(scores.values())) if tag != "__overall__")
    with (output_dir / f"{split}_f1.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["tag", *scores])
        for tag in tags:
            writer.writerow([tag, *(f"{scores[name][tag]:.6f}" for name in scores)])
        writer.writerow(["__overall_accuracy__", *(f"{scores[name]['__overall__']:.6f}" for name in scores)])
    if not plots:
        return
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed; CSV results were written.")
        return
    figure, axis = plt.subplots(figsize=(max(10, len(tags) * 0.35), 6))
    positions = list(range(len(tags)))
    width = 0.8 / len(scores)
    for offset, (name, values) in enumerate(scores.items()):
        axis.bar([p + offset * width for p in positions], [values[tag] for tag in tags], width=width, label=name)
    axis.set_xticks([p + width * (len(scores) - 1) / 2 for p in positions])
    axis.set_xticklabels(tags, rotation=75, ha="right")
    axis.set_ylim(0, 1)
    axis.set_ylabel("F1-score")
    axis.set_title(f"Hindi POS tagging - {split} per-tag F1")
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_dir / f"{split}_f1.png", dpi=150)
    plt.close(figure)
