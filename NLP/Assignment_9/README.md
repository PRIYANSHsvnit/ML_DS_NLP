# NLP Assignment 9: Hindi POS Tagging

This implementation follows the PDF requirement to compare:

1. A Maximum Entropy Markov Model (MEMM) using NLTK's MaxEnt classifier.
2. A linear-chain Conditional Random Field (CRF) using `sklearn-crfsuite`.
3. The Naive Bayes and HMM baselines developed in Assignment 7.

## Project structure

| File | Responsibility |
| --- | --- |
| `data.py` | Streaming `WORD TAG` corpus reader and bounds |
| `features.py` | Required prefixes, suffixes, context, and binary length features |
| `memm.py` | NLTK MaxEnt MEMM with autoregressive previous-tag features |
| `crf.py` | Linear-chain CRF trainer and decoder |
| `naive_bayes.py`, `hmm.py` | Assignment 7 baseline implementations |
| `evaluation.py` | Per-tag F1 and overall accuracy |
| `reporting.py` | CSV, JSON, and bar-chart output |
| `experiment.py` | Ordered, one-model-at-a-time experiment runner |
| `main.py` | Command-line entry point |
| `viewer.py` | Terminal summary and optional HTML viewer |
| `REPORT.md` | Method, resource, result, and justification write-up |

## Installation and execution

From this directory:

```powershell
python -m pip install -r requirements.txt
python main.py
python viewer.py --results outputs/results.json --html outputs/results.html
```

The default run is intentionally bounded to 5,000 training sentences and 300
evaluation sentences. This produces a useful comparison without launching all
training jobs at once or monopolising the CPU. For the complete corpus, run:

```powershell
python main.py --full-dataset --output-dir outputs-full
```

For a fast smoke run:

```powershell
python main.py --max-train-sentences 200 --max-eval-sentences 30 \
  --memm-iterations 3 --crf-iterations 10 --skip-plots
```

Each model is trained and released sequentially. The corpus is streamed from
disk for the baselines and MEMM, evaluation processes one sentence at a time,
and no multiprocessing or deep-learning model is used. The CRF uses the
assignment's requested feature set and bounded L-BFGS iterations rather than a
larger neural model, which is the appropriate model choice for this rubric.

Generated files:

- `outputs/results.json`: configuration, timings, explanations, and scores.
- `outputs/dev_metrics.csv`, `outputs/test_metrics.csv`: per-tag F1 and accuracy.
- `outputs/*_per_tag_f1.png`: comparative bar charts.
- `outputs/results.html`: optional browser-friendly summary.
