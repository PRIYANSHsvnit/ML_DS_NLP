# Assignment 7 Report: Hindi POS Tagging

## 1. Objective

The task is to predict the part-of-speech tag of every Hindi word using:

1. A Naive Bayes classifier with word length, actual word, previous word, next
   word, and previous tag features.
2. A Hidden Markov Model with forward Viterbi, backward Viterbi, and
   forward-backward Viterbi decoding.

The train, development, and test files are kept separate. The development
split is used for comparison during experimentation; the test split is used
only for the final reported result.

## 2. Data processing

Each non-empty line has the form `WORD TAG`. Blank lines mark sentence
boundaries. `data.py` reads the files as UTF-8 and yields one sentence at a
time. This avoids making a second full in-memory copy of the corpus.

The observed corpus contains:

| Split | Sentences | Tokens |
|---|---:|---:|
| Train | 15,087 | 325,710 |
| Dev | 1,866 | 40,762 |
| Test | 1,910 | 41,415 |

## 3. Naive Bayes model

For each token, the feature vector is:

```text
(length, word, previous_word, next_word, previous_tag)
```

The length feature is `MORE` when the word has more than four characters and
`LESS` otherwise. The previous tag is the tag predicted immediately before the
current word, so decoding is sequential.

For tag `t`, the classifier maximizes the sum of log probabilities:

```text
log P(t) + sum_f log P(feature_f | t)
```

Additive smoothing with `alpha = 0.1` prevents zero probabilities for unseen
words, contexts, and feature values.

## 4. HMM model

The HMM estimates:

```text
P(tag_i | tag_{i-1})       transition probability
P(word_i | tag_i)          emission probability
```

Sentence start and end markers are included in transition counts. All
calculations use logarithms, which prevents underflow on long Hindi
sentences. Additive smoothing is again used for unseen transitions and
emissions.

### Decoders

- **Forward Viterbi:** fills the dynamic-programming table left to right and
  backtracks from the best final tag.
- **Backward Viterbi:** computes the best suffix score right to left and
  reconstructs the sequence from the best starting tag.
- **Forward-backward Viterbi:** computes forward and backward scores and
  selects the highest combined score at each position.

The HMM complexity is `O(n × T²)` per sentence, where `n` is sentence length
and `T` is the number of POS tags. This is the required exact dynamic
program; no expensive all-corpus CPU parallelism is introduced.

## 5. Evaluation

For each tag:

```text
precision = TP / (TP + FP)
recall    = TP / (TP + FN)
F1        = 2 × precision × recall / (precision + recall)
```

The CSV files contain F1 for every tag. The final row contains token accuracy,
which is also printed by the runner. Charts compare the per-tag F1 values.

## 6. Final results

The full run used all available training, development, and test sentences.

| Algorithm | Dev accuracy | Test accuracy |
|---|---:|---:|
| Naive Bayes | 0.9247 | 0.9257 |
| HMM forward Viterbi | 0.9305 | 0.9285 |
| HMM backward Viterbi | 0.9305 | 0.9285 |
| HMM forward-backward Viterbi | 0.9305 | 0.9285 |

The detailed per-tag results are in `results/dev_f1.csv` and
`results/test_f1.csv`. The corresponding visual comparisons are
`results/dev_f1.png` and `results/test_f1.png`.

## 7. Interpretation and justification

The HMM is the best overall choice because it models tag-to-tag sequence
structure in addition to word evidence. This is especially useful for
context-sensitive Hindi tags. Naive Bayes is competitive because the actual
word and neighboring-word features are informative, but it does not represent
the complete tag sequence probability as directly as the HMM.

The three HMM decoders produce the same aggregate result on this corpus. This
is a useful consistency check: the independently implemented directions
recover the same high-scoring sequence for the evaluated sentences. Small
per-tag differences may still be visible in the CSV when tied or near-tied
paths occur.

A transformer was not selected. The assignment requires these classical
algorithms, and replacing them with a pretrained model would not provide a
valid comparison. The selected implementation is more reproducible for
evaluation, requires no model download, and uses substantially less CPU and
memory.

## 8. Reproducibility

```powershell
cd NLP\Asssignment_7
python main.py
python viewer.py --results-dir results
```

The runner executes sequentially and prints progress, algorithm accuracy, and
the output location. `--max-train-sentences`, `--max-eval-sentences`, and
`--max-eval-tokens` can be used for a bounded smoke test before the full run.
