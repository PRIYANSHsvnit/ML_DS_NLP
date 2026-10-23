# Assignment 9 Report

## Objective

The Hindi POS corpus from Assignment 7 is used to compare a Maximum Entropy
Markov Model (MEMM), a Conditional Random Field (CRF), Naive Bayes, and an HMM
on the development and test splits.

## Feature design

The shared feature extractor in `features.py` supplies:

- Prefixes of lengths 1, 2, 3, and 4.
- Suffixes of lengths 1, 2, 3, and 4; `NULL` is used when the word is shorter
  than the requested length.
- Previous, current, and next word.
- `LESS` when word length is at most four, otherwise `MORE`.
- Previous tag for the MEMM, with an explicit `<START>` boundary.

The CRF receives these observations for every token and learns transition
weights globally. The MEMM predicts left-to-right and feeds its previous
prediction into the next local MaxEnt decision.

## Model comparison

Naive Bayes and HMM are retained as the Assignment 7 baselines. The HMM uses
smoothed transition and emission probabilities with Viterbi decoding. Naive
Bayes uses the same feature-oriented baseline from Assignment 7. Accuracy is
reported alongside per-tag F1:

\[
F1_t = \frac{2TP_t}{2TP_t + FP_t + FN_t}
\]

The output CSV files contain one row per tag and an overall accuracy row. The
PNG files compare all four models for every tag, as required by the PDF.

## Resource and model justification

The default runner is deliberately sequential: it trains exactly one model,
then evaluates all requested splits, before starting the next model. This
avoids four concurrent optimisers competing for CPU and memory. Input is
streamed and evaluation is sentence-at-a-time. Training and evaluation bounds
are command-line options, with a safe default of 5,000 training sentences and
300 evaluation sentences. `--full-dataset` is available when a complete
submission run is required.

The CRF is the strongest model for this assignment because it models
dependencies between neighboring tags without the label-bias limitation of a
locally-normalized MEMM. The MEMM is still implemented because it is explicitly
required. A transformer is not substituted: it would add substantial resource
cost and would not answer the specified classical-model comparison.

## Reproducibility

Install `requirements.txt`, run `main.py`, and then run `viewer.py`. The JSON
file records the bounds, optimizer iterations, model training times, token
counts, scores, and explanations used to interpret the result.
