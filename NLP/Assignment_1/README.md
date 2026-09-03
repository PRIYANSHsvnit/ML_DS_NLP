# NLP Assignment 1
## IndicCorpV2 Corpus Processing and Corpus Statistics

---

## Objective

The objective of this assignment is to perform basic Natural Language Processing (NLP) tasks on the **IndicCorpV2** dataset.

The assignment includes:

- Downloading the dataset for the selected language.
- Implementing a custom sentence tokenizer.
- Implementing a custom word tokenizer.
- Tokenizing the corpus.
- Saving the processed data.
- Computing various corpus statistics.

---

# Dataset Used

**Dataset Name**

- IndicCorpV2

**Source**

https://huggingface.co/datasets/ai4bharat/IndicCorpV2

**Language Used**

- Hindi (`hin_Deva`)

---

# Dataset Download

The complete Hindi corpus is approximately **2 GB**.

Instead of downloading the entire dataset, the first parquet shard (`0000.parquet`) was downloaded from the Hugging Face parquet conversion.

For this assignment, only the **first 10,000 samples** were extracted and saved as:

```
data/raw/indic_raw.parquet
```

This reduces execution time while preserving a sufficiently large corpus for experimentation.

---

# Libraries Used

| Library | Purpose |
|----------|---------|
| datasets | Load Hugging Face datasets |
| huggingface_hub | Download dataset files |
| pandas | Store tokenized data into parquet format |
| pathlib | Platform-independent file handling |
| regex / re | Sentence and word tokenization |

---

# Project Structure

```
Assignment_1
│
├── data
│   └── raw
│       ├── indic_raw.parquet
│       └── hi
│           └── partial
│               └── train
│                   └── 0000.parquet
│
├── output
│   ├── indic.parquet
│   ├── indic_statistics.txt
│   └── indic_tokenized.txt
│
├── src
│   ├── download_data.py
│   ├── tokenizer.py
│   ├── preprocessor.py
│   └── statistics.py
│
├── main.py
└── README.md
```

---

# File Description

## download_data.py

Responsible for:

- Downloading IndicCorpV2 Hindi parquet shard
- Loading the dataset
- Selecting first 10,000 samples
- Saving the sampled dataset

Output:

```
data/raw/indic_raw.parquet
```

---

## tokenizer.py

Contains two custom tokenizers.

### Sentence Tokenizer

Splits paragraphs into sentences using:

- `.`
- `!`
- `?`
- Hindi danda (`।`)

### Word Tokenizer

Handles:

- Hindi words
- English words
- URLs
- Email IDs
- Integers
- Decimal numbers
- Dates
- Punctuation symbols

Examples:

```
https://abc.com

abc@gmail.com

12.45

25/07/2026

भारत

,
.
?
!
```

---

## preprocessor.py

Processes the complete dataset.

Steps:

1. Read every paragraph.
2. Split paragraph into sentences.
3. Split sentences into words.
4. Save tokenized sentences.

Outputs

```
output/indic_tokenized.txt
```

One tokenized sentence per line.

Also saves

```
output/indic.parquet
```

---

## statistics.py

Computes corpus statistics.

Statistics computed:

1. Total Sentences
2. Total Words
3. Total Characters
4. Average Sentence Length
5. Average Word Length
6. Type Token Ratio (TTR)

Results are stored in

```
output/indic_statistics.txt
```

---

## main.py

Main execution file.

Pipeline:

```
Load Dataset

↓

Sentence Tokenization

↓

Word Tokenization

↓

Save Tokenized Corpus

↓

Compute Corpus Statistics

↓

Save Statistics
```

---

# Output Files

## indic_tokenized.txt

Contains one tokenized sentence per line.

Example:

```
भारत एक महान देश है ।
मेरा नाम राहुल है ।
```

---

## indic.parquet

Stores tokenized sentences in compressed parquet format.

---

## indic_statistics.txt

Contains corpus statistics such as

```
Total Sentences

Total Words

Total Characters

Average Sentence Length

Average Word Length

Type Token Ratio
```

---

# Corpus Statistics Formulae

### Average Sentence Length

```
Average Sentence Length =
Total Words / Total Sentences
```

---

### Average Word Length

```
Average Word Length =
Total Characters / Total Words
```

---

### Type Token Ratio (TTR)

```
TTR =
Unique Words / Total Words
```

Higher TTR indicates richer vocabulary.

---

# Requirements

Install required libraries:

```bash
pip install datasets
pip install huggingface_hub
pip install pandas
pip install pyarrow
```

---

# Running the Project

If dataset is already downloaded:

```bash
python main.py
```

If downloading the dataset for the first time, uncomment the download section in `main.py`, execute it once, and then comment it again for future runs.

---

# Note

Only the first **10,000 Hindi samples** were processed for this assignment.

The same preprocessing pipeline can be reused for other Indic languages or larger corpora by changing the dataset source.

---

# Future Work

- Process the complete IndicCorpV2 dataset.
- Apply the same pipeline to OSCAR-2301.
- Add stemming and lemmatization.
- Compute additional lexical statistics.
- Build an n-gram language model.

---