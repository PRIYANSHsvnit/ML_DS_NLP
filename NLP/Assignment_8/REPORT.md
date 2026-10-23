# Assignment 8 Report

## 1. Scope

The lab PDF asks for programs for the five midsem questions and a noisy
channel spell-correction model. Each midsem question is isolated in its own
module under `midsem_solutions/`, and `main.py` runs them in the required
sequence together with spell correction. The midsem portion can also be run
independently with `python -m midsem_solutions.main`.

## 2. Midsem solutions

### Q1: FST noun pluralization

The transducer copies the noun. The regular path emits `s`; the exception path
emits `es` when the noun ends in `s`, `x`, `z`, `ch`, or `sh`. A singular path
emits the lexical form with `+SG+N`, and the plural path represents `+PL+N`.
Examples produced by the program include `cat -> cats`, `box -> boxes`, and
`church -> churches`.

### Q2: WordPiece

The corpus is represented as character symbols plus `</w>`. Pair frequencies
are counted with word frequencies, and two greedy merges are applied:

1. `(l, o)` with frequency 10
2. `(lo, w)` with frequency 10

`newest` is therefore tokenized as
`n e w e s t </w>` after these two merges.

### Q3: TF-IDF

For each sentence, TF is the raw term count and:

```text
IDF(word) = log(N / document_frequency(word))
TF-IDF(word) = TF(word) * IDF(word)
```

Cosine similarity is used for sentence comparison. The closest pair is
Sentence 1 and Sentence 3. The complete vocabulary, IDF values, vectors, and
pairwise similarities are stored in `outputs/results.json`.

### Q4: Bernoulli Naive Bayes

For query `(free=0, win=0, offer=0)`, each class score is:

```text
P(class) * P(free=0 | class) * P(win=0 | class) * P(offer=0 | class)
```

The resulting prediction is **NotSpam**. The full prior and likelihood
calculation is serialized in the result file.

### Q5: Kneser-Ney

For discount `d=0.5`, the implementation uses:

```text
P_KN(w|h) = max(c(hw)-d, 0)/c(h) + lambda(h) P_continuation(w)
```

The requested values are:

| Probability | Value |
|---|---:|
| `P_KN(AI | love)` | 0.375 |
| `P_KN(NLP | like)` | 0.875 |

No sentence boundary markers are added.

## 3. Spell correction

The spell checker uses the noisy-channel objective:

```text
argmax_candidate log P(error | candidate) + log P(candidate)
```

Candidate words are generated at edit distance one and filtered against the
provided unigram vocabulary. The supplied `count_1edit.txt` character-edit
frequencies provide channel evidence; unigram frequencies provide the language
prior. Candidate generation is capped at 64 candidates per token.

On the supplied Holbrook tagged-error file, the current run evaluated 2,599
errors and corrected 629:

```text
accuracy = 629 / 2599 = 0.242016
```

This is a transparent baseline: the file contains varied real learner errors,
including errors beyond one edit and context-dependent corrections. The
implementation does not use the gold target while predicting.

## 4. Resource and model justification

The assignment specifies classical algorithms, so a transformer is not an
appropriate replacement. It would add model downloads, memory pressure, and
unrequested behavior while preventing a faithful answer to the formulas.
The selected approach is deterministic and reproducible:

- experiments run sequentially, with no multiprocessing or queued batches;
- large files are read once and the spell evaluation processes examples in a
  bounded loop;
- no neural framework is imported;
- candidate generation is bounded to prevent pathological CPU work;
- JSON preserves all intermediate calculations, while the HTML viewer makes
  the result easy to demonstrate.

Run:

```powershell
python main.py
python viewer.py --results outputs/results.json --html outputs/results.html
```
