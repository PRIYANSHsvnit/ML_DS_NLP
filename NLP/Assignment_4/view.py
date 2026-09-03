from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent

DB = BASE_DIR / "ngram_model.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()


def word(word_id):
    cur.execute(
        "SELECT word FROM vocab WHERE id = ?",
        (word_id,)
    )

    result = cur.fetchone()

    return result[0] if result else "UNK"


# TABLES

print("\nTABLES")
print("=" * 60)

cur.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
""")

for row in cur.fetchall():
    print(row[0])


# VOCABULARY

print("\nVOCABULARY")
print("=" * 60)

cur.execute("""
    SELECT word, id
    FROM vocab
    LIMIT 20
""")

for w, i in cur.fetchall():
    print(f"{i:5} -> {w}")


# UNIGRAMS

print("\nUNIGRAMS")
print("=" * 60)

cur.execute("""
    SELECT w, c
    FROM unigram
    ORDER BY c DESC
    LIMIT 20
""")

for w, c in cur.fetchall():
    print(
        f"{word(w):20} -> {c}"
    )


# BIGRAMS

print("\nBIGRAMS")
print("=" * 60)

cur.execute("""
    SELECT w1, w2, c
    FROM bigram
    ORDER BY c DESC
    LIMIT 20
""")

for w1, w2, c in cur.fetchall():
    print(
        f"({word(w1)}, {word(w2)}) -> {c}"
    )


# TRIGRAMS

print("\nTRIGRAMS")
print("=" * 60)

cur.execute("""
    SELECT w1, w2, w3, c
    FROM trigram
    ORDER BY c DESC
    LIMIT 20
""")

for w1, w2, w3, c in cur.fetchall():
    print(
        f"({word(w1)}, {word(w2)}, {word(w3)}) -> {c}"
    )


# QUADRIGRAMS

print("\nQUADRIGRAMS")
print("=" * 60)

cur.execute("""
    SELECT w1, w2, w3, w4, c
    FROM quadrigram
    ORDER BY c DESC
    LIMIT 20
""")

for w1, w2, w3, w4, c in cur.fetchall():
    print(
        f"({word(w1)}, {word(w2)}, "
        f"{word(w3)}, {word(w4)}) -> {c}"
    )


# COUNTS

print("\nDATABASE SIZES")
print("=" * 60)

for table in [
    "vocab",
    "unigram",
    "bigram",
    "trigram",
    "quadrigram"
]:

    cur.execute(
        f"SELECT COUNT(*) FROM {table}"
    )

    count = cur.fetchone()[0]

    print(
        f"{table:<15} : {count:,}"
    )


conn.close()