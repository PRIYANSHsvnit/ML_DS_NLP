# NLP Assignment 10

This implementation compares Google News Word2Vec, GloVe, and FastText on the
Amazon reviews task in the PDF. It performs the required lowercase,
punctuation/number removal, tokenization, and stopword removal; takes
stratified 10,000/1,000 train/test samples; evaluates word analogies; and
trains one-hidden-layer neural networks using both unweighted and TF-IDF
weighted sentence vectors.

## Run

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

After placing the files in the locations below, run from this directory. The
defaults are already configured (the Word2Vec file is the standalone
`GoogleNews-vectors-negative300.bin`; GloVe and FastText are word2vec-format
text files):

```powershell
python main.py
```

You can override any path with `--train`, `--test`, `--word2vec`, `--glove`,
`--fasttext`, or `--analogy`.

The default evaluates every compatible analogy row. For a quick smoke test,
add `--train-size 200 --test-size 50 --max-analogies 100`.

Loading the full FastText file can take several minutes because it is over
2 GB. To demonstrate the evaluator quickly without loading every embedding,
run only Word2Vec:

```powershell
python main.py --embeddings word2vec --train-size 100 --test-size 20 `
  --max-analogies 20 --output-dir outputs-demo
```

The complete assignment still runs all three models with the default command.

The included Amazon files are headerless CSVs with columns
`label,title,review`; the loader detects this format and streams the file twice
to perform exact stratified reservoir sampling without holding the 1.5 GB
training CSV in RAM.

The runner is intentionally sequential: only one embedding and one classifier
are active at a time. It limits BLAS/OpenMP pools to two threads, uses
mini-batches and early stopping, evaluates only the requested sample sizes,
and releases each embedding before loading the next one. Each embedding is
loaded only during its sequential turn, so Q2 searches the complete
vocabulary rather than a review-only subset. This uses more memory during one
embedding's turn, but avoids incorrect analogy results.

## Required files and paste locations

Create these folders inside this Assignment 10 directory:

```text
data\
  amazon\
    train.csv
    test.csv
  embeddings\
    GoogleNews-vectors-negative300.bin
    glove.6B.300d.txt
    wiki-news-300d-1M-subword.vec
  analogies\
    questions-words.txt
```

Download and extract the Amazon dataset from the Kaggle link in the PDF, then
place its `train.csv` and `test.csv` in `data\amazon\`. Put the extracted
Google News Word2Vec `.bin`, GloVe text file, FastText `.vec` file, and
`questions-words.txt` in the exact locations above. Kaggle downloads normally
require your browser login/API credentials, and the embedding files are very
large, so manual download is safer than silently starting multi-gigabyte
downloads.

Results, including dimensions, analogy accuracy, macro F1, and timings, are
written to `outputs/results.json`. The classical one-hidden-layer MLP is the
best fit for the assignment: it directly satisfies the rubric while avoiding
the CPU and memory cost of a transformer.
