# NLP Assignment 7: Hindi POS Tagging

This folder contains a complete, reproducible implementation of the PDF
assignment. The code is deliberately split into topic-wise files instead of
putting every algorithm in one script.

## Project structure

| File | Responsibility |
|---|---|
| `data.py` | Streaming `WORD TAG` corpus reader and bounded iterators |
| `probability.py` | Shared additive-smoothed log probability helper |
| `naive_bayes.py` | Naive Bayes classifier with the five required features |
| `hmm.py` | HMM training and the three required Viterbi decoders |
| `evaluation.py` | Per-tag F1 and overall accuracy calculation |
| `reporting.py` | CSV output and comparison chart generation |
| `experiment.py` | Ordered experiment pipeline |
| `main.py` | Small command-line entry point |
| `viewer.py` | Terminal summary viewer for generated results |
| `REPORT.md` | Assignment explanation, formulas, results, and justification |

## Run the complete experiment

From this directory:

```powershell
python main.py
```

The sequence is:

1. Stream and train Naive Bayes.
2. Stream and train the HMM.
3. Evaluate all algorithms on development data.
4. Evaluate all algorithms on test data.
5. Write CSV metrics and PNG charts.

Results are written to `results/`:

- `dev_f1.csv`, `test_f1.csv`: per-tag F1 scores and overall accuracy.
- `dev_f1.png`, `test_f1.png`: visual comparison across all POS tags.

View the generated results in the terminal:

```powershell
python viewer.py --results-dir results
```

## Resource-conscious execution

The pipeline does not use multiprocessing or a deep-learning framework. It
reads one sentence at a time, stores sparse count tables, evaluates one
sentence at a time, and uses log probabilities. This keeps memory bounded and
prevents all sentences from being queued on the CPU simultaneously. The HMM
uses the required dynamic-programming cost of `O(sentence_length × tags²)`;
there is no avoidable parallel CPU workload.

Run a quick bounded experiment:

```powershell
python main.py --max-train-sentences 500 --max-eval-sentences 100 --skip-plots
```

Options:

```text
--data-dir PATH              POS data directory
--output-dir PATH            Results directory
--alpha FLOAT                Additive smoothing value (default: 0.1)
--max-train-sentences N      Train on only N sentences
--max-eval-sentences N       Evaluate only N sentences
--max-eval-tokens N          Evaluate only N tokens
--skip-plots                 Write CSVs without rendering charts
```

The assignment specifically asks for Naive Bayes and HMM algorithms, so a
transformer is not substituted. A transformer would make the comparison
invalid and add unnecessary CPU/memory requirements.
