# Assignment 5 — N-gram Smoothing

This implementation is designed for the existing SQLite-based n-gram setup
(`ngram_model.db`) and the 1M-row tokenized corpus (`indic_tokenized.txt`).

## Files

- `data_loader.py` — streaming corpus reader + train/dev/test split
- `ngram_model.py` — SQLite counts + all smoothing implementations
- `main.py` — creates splits and builds 1–4 gram database
- `evaluation.py` — evaluates Interpolation, Good-Turing, Katz, Stupid Backoff and Kneser-Ney
- `view.py` — result tables and plots

## Expected corpus format

One tokenized sentence per line:

```text
यह एक उदाहरण है
मुझे मशीन लर्निंग पसंद है
```

If `indic_tokenized.txt` already contains one tokenized sentence per line,
the code can be used directly.

## 1. Build

First run a small sanity build if the corpus is huge:

```powershell
python main.py --data indic_tokenized.txt --db ngram_model.db --rebuild-split --rebuild-db
```

This creates:

```text
splits/
    train.txt
    dev.txt
    test.txt
```

Default split:

- 80% train
- 10% development
- 10% test

The split is deterministic with seed 42.

## 2. Quick evaluation test

Before running the complete 1M-row evaluation:

```powershell
python evaluation.py --db ngram_model.db --max-sentences 1000
```

This is only a sanity check.

## 3. Full development + test evaluation

```powershell
python evaluation.py --db ngram_model.db
```

Outputs:

```text
results/
    development_results.csv
    test_results.csv
```

## 4. Visual comparison

```powershell
python view.py --csv results/test_results.csv
```

Outputs:

```text
results/plots/
    test_perplexity_comparison.png
    test_perplexity_by_order.png
```

## 5. Development-set tuning

### Interpolation

For a bigram:

```python
from evaluation import tune_interpolation_on_dev

best = tune_interpolation_on_dev(
    "ngram_model.db",
    "splits/dev.txt",
    order=2,
    step=0.10,
)
print(best)
```

For a trigram or quadgram, change `order`.

### Kneser-Ney discount

```python
from evaluation import tune_simple_parameter

best = tune_simple_parameter(
    "ngram_model.db",
    "splits/dev.txt",
    method="kneser_ney",
    order=4,
    values=[0.50, 0.60, 0.70, 0.75, 0.80, 0.90],
    parameter_name="D",
)
print(best)
```

### Stupid Backoff alpha

```python
best = tune_simple_parameter(
    "ngram_model.db",
    "splits/dev.txt",
    method="stupid_backoff",
    order=4,
    values=[0.2, 0.3, 0.4, 0.5, 0.6],
    parameter_name="alpha",
)
print(best)
```

## Important evaluation note

Stupid Backoff does not produce a normalized probability distribution.
Therefore its pseudo-perplexity should NOT be presented as directly equivalent
to the true probabilistic perplexity of Interpolation, Good-Turing, Katz or
Kneser-Ney.

For the report:

- compare normalized methods with standard test perplexity;
- report Stupid Backoff using average log-score / ranking score;
- explicitly mention this theoretical limitation.

## Recommended report table

Use:

| Order | Method | Dev PPL | Test PPL | Zero Probability Events | Time |
|---|---|---:|---:|---:|---:|
| 2 | Interpolation | ... | ... | ... | ... |
| 2 | Good-Turing | ... | ... | ... | ... |
| 2 | Katz | ... | ... | ... | ... |
| 2 | Stupid Backoff | N/A* | N/A* | ... | ... |
| 2 | Kneser-Ney | ... | ... | ... | ... |

Repeat for Trigram and Quadgram.

*Stupid Backoff does not have a normalized probability distribution.

## Reproducibility

All final test results should be generated only after selecting parameters
on the development set. Do not tune against the test set.

The default example weights:

- Bigram interpolation: 0.20, 0.80
- Trigram interpolation: 0.10, 0.25, 0.65
- Quadgram interpolation: 0.05, 0.15, 0.25, 0.55

and:

- Stupid Backoff alpha = 0.40
- Kneser-Ney D = 0.75

are starting values, not claimed optimal values. Report the values actually
selected using your development set.

## Numerical fixes in this revision

- Evaluation keeps the same three start markers used when the shared 1–4-gram
  database is built, then removes only the extra markers for lower-order tests.
  This prevents bigram/trigram evaluation from predicting a start marker.
- The unsmoothed MLE baseline is implemented explicitly. Infinite MLE perplexity
  is expected when the test set contains unseen n-grams.
- Interpolation renormalizes its weights when a higher-order context is unseen.
- Good-Turing backs off when a context has no singleton followers, where its
  local unseen-event estimate is unavailable. Sparse count-of-counts estimates
  use a conservative half-count discount rather than silently leaving Katz
  with no backoff mass. This fallback should be described in the report as a
  practical sparse-data safeguard, not as the exact textbook Simple Good-Turing
  regression estimator.
- Katz uses a finite uniform fallback if its lower-order unseen mass is
  numerically zero.
- Stupid Backoff remains a non-normalized score; its pseudo-perplexity is not
  comparable to standard perplexity.

After replacing the scripts, rebuild the database to ensure its count and
statistics tables are consistent:

```powershell
python main.py --data indic_tokenized.txt --db ngram_model.db --rebuild-split --rebuild-db
```
