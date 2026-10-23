# NLP Assignment 8

This solution covers both parts of the lab PDF:

1. The five midsem questions are implemented independently in the
   `midsem_solutions/` folder.
2. `spell_correction/` implements a noisy-channel spell checker using the
   supplied unigram and one-edit counts and evaluates it on the tagged
   Holbrook errors.

## Run

From this directory:

```powershell
python main.py
python viewer.py --results outputs/results.json --html outputs/results.html
```

For a fast smoke test, limit the spell-correction evaluation:

```powershell
python main.py --max-spell-errors 200
```

## Design and resource control

The runner executes topics sequentially. It does not start worker processes,
load a neural model, or queue the corpus onto the CPU. The spell checker reads
the large count files once and bounds generated candidates to 64 per error.
The midsem calculations are tiny deterministic computations. This is the
appropriate model choice for this assignment: the rubric explicitly asks for
classical FST, WordPiece, TF-IDF, Naive Bayes, Kneser–Ney, and noisy-channel
methods; a transformer would be slower, less reproducible, and not answer the
specified questions.

`outputs/results.json` contains the complete computations and explanations.
`viewer.py` prints a terminal summary and can produce a dependency-free HTML
viewer for evaluation/demo.

## Run only the midsem solutions

```powershell
python -m midsem_solutions.main
```

This writes `midsem_outputs.json` inside `midsem_solutions/`. The combined
`python main.py` runner also executes these five solutions before the spell
correction experiment.
