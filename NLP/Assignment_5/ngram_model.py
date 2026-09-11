import sqlite3
from collections import Counter


K = 0.3


class NGramModel:

    def __init__(self, db_file="ngram_model.db"):
        self.conn = sqlite3.connect(db_file)
        self.cur = self.conn.cursor()

        self.create_tables()

        self.vocab_size = 0
        self.total_tokens = 0

        self.word_cache = {}
        self.next_word_id = 0

    # =========================================================
    # DATABASE
    # =========================================================

    def create_tables(self):

        self.cur.executescript("""
            CREATE TABLE IF NOT EXISTS vocab (
                word TEXT PRIMARY KEY,
                id INTEGER UNIQUE
            );

            CREATE TABLE IF NOT EXISTS unigram (
                w INTEGER PRIMARY KEY,
                c INTEGER
            );

            CREATE TABLE IF NOT EXISTS bigram (
                w1 INTEGER,
                w2 INTEGER,
                c INTEGER,
                PRIMARY KEY (w1, w2)
            );

            CREATE TABLE IF NOT EXISTS trigram (
                w1 INTEGER,
                w2 INTEGER,
                w3 INTEGER,
                c INTEGER,
                PRIMARY KEY (w1, w2, w3)
            );

            CREATE TABLE IF NOT EXISTS quadrigram (
                w1 INTEGER,
                w2 INTEGER,
                w3 INTEGER,
                w4 INTEGER,
                c INTEGER,
                PRIMARY KEY (w1, w2, w3, w4)
            );

            CREATE TABLE IF NOT EXISTS bigram_context (
                w1 INTEGER PRIMARY KEY,
                c INTEGER
            );

            CREATE TABLE IF NOT EXISTS trigram_context (
                w1 INTEGER,
                w2 INTEGER,
                c INTEGER,
                PRIMARY KEY (w1, w2)
            );

            CREATE TABLE IF NOT EXISTS quadrigram_context (
                w1 INTEGER,
                w2 INTEGER,
                w3 INTEGER,
                c INTEGER,
                PRIMARY KEY (w1, w2, w3)
            );
        """)

        self.conn.commit()

    # =========================================================
    # RESET
    # =========================================================

    def reset(self):

        self.cur.executescript("""
            DELETE FROM vocab;
            DELETE FROM unigram;
            DELETE FROM bigram;
            DELETE FROM trigram;
            DELETE FROM quadrigram;

            DELETE FROM bigram_context;
            DELETE FROM trigram_context;
            DELETE FROM quadrigram_context;
        """)

        self.conn.commit()

        self.word_cache.clear()
        self.next_word_id = 0

    # =========================================================
    # WORD ID - TRAINING
    # =========================================================

    def word_id(self, word):

        if word in self.word_cache:
            return self.word_cache[word]

        word_id = self.next_word_id

        self.word_cache[word] = word_id
        self.next_word_id += 1

        self.cur.execute(
            "INSERT INTO vocab(word, id) VALUES (?, ?)",
            (word, word_id)
        )

        return word_id

    # =========================================================
    # WORD ID - EVALUATION
    # =========================================================

    def get_id(self, word):

        if word in self.word_cache:
            return self.word_cache[word]

        self.cur.execute(
            "SELECT id FROM vocab WHERE word = ?",
            (word,)
        )

        result = self.cur.fetchone()

        if result is None:
            return -1

        self.word_cache[word] = result[0]

        return result[0]

    # =========================================================
    # TRAIN
    # =========================================================

    def train(
        self,
        filename,
        dev_indices,
        test_indices,
        batch_size=5000
    ):

        uni = Counter()
        bi = Counter()
        tri = Counter()
        quad = Counter()

        bi_ctx = Counter()
        tri_ctx = Counter()
        quad_ctx = Counter()

        sentence_count = 0

        with open(filename, encoding="utf-8") as f:

            for i, line in enumerate(f):

                if i in dev_indices or i in test_indices:
                    continue

                sentence = line.strip()

                if not sentence:
                    continue

                words = (
                    ["<BOS>"]
                    + sentence.split()
                    + ["<EOS>"]
                )

                ids = [
                    self.word_id(word)
                    for word in words
                ]

                uni.update(ids)

                for j in range(len(ids) - 1):

                    w1 = ids[j]
                    w2 = ids[j + 1]

                    bi[(w1, w2)] += 1
                    bi_ctx[w1] += 1

                for j in range(len(ids) - 2):

                    w1 = ids[j]
                    w2 = ids[j + 1]
                    w3 = ids[j + 2]

                    tri[(w1, w2, w3)] += 1
                    tri_ctx[(w1, w2)] += 1

                for j in range(len(ids) - 3):

                    w1 = ids[j]
                    w2 = ids[j + 1]
                    w3 = ids[j + 2]
                    w4 = ids[j + 3]

                    quad[(w1, w2, w3, w4)] += 1
                    quad_ctx[(w1, w2, w3)] += 1

                sentence_count += 1

                if sentence_count % batch_size == 0:

                    self.save_batch(
                        uni,
                        bi,
                        tri,
                        quad,
                        bi_ctx,
                        tri_ctx,
                        quad_ctx
                    )

                    uni.clear()
                    bi.clear()
                    tri.clear()
                    quad.clear()

                    bi_ctx.clear()
                    tri_ctx.clear()
                    quad_ctx.clear()

                    print(
                        f"Training: "
                        f"{sentence_count:,}/998,000"
                    )

        if uni:

            self.save_batch(
                uni,
                bi,
                tri,
                quad,
                bi_ctx,
                tri_ctx,
                quad_ctx
            )

        self.calculate_statistics()

    # =========================================================
    # SAVE BATCH
    # =========================================================

    def save_batch(
        self,
        uni,
        bi,
        tri,
        quad,
        bi_ctx,
        tri_ctx,
        quad_ctx
    ):

        self.cur.executemany(
            """
            INSERT INTO unigram(w, c)
            VALUES (?, ?)

            ON CONFLICT(w)
            DO UPDATE SET c = c + excluded.c
            """,
            uni.items()
        )

        self.cur.executemany(
            """
            INSERT INTO bigram(w1, w2, c)
            VALUES (?, ?, ?)

            ON CONFLICT(w1, w2)
            DO UPDATE SET c = c + excluded.c
            """,
            [
                (a, b, c)
                for (a, b), c in bi.items()
            ]
        )

        self.cur.executemany(
            """
            INSERT INTO trigram(w1, w2, w3, c)
            VALUES (?, ?, ?, ?)

            ON CONFLICT(w1, w2, w3)
            DO UPDATE SET c = c + excluded.c
            """,
            [
                (a, b, c, d)
                for (a, b, c), d in tri.items()
            ]
        )

        self.cur.executemany(
            """
            INSERT INTO quadrigram(
                w1, w2, w3, w4, c
            )
            VALUES (?, ?, ?, ?, ?)

            ON CONFLICT(w1, w2, w3, w4)
            DO UPDATE SET c = c + excluded.c
            """,
            [
                (a, b, c, d, e)
                for (a, b, c, d), e in quad.items()
            ]
        )

        self.cur.executemany(
            """
            INSERT INTO bigram_context(w1, c)
            VALUES (?, ?)

            ON CONFLICT(w1)
            DO UPDATE SET c = c + excluded.c
            """,
            bi_ctx.items()
        )

        self.cur.executemany(
            """
            INSERT INTO trigram_context(w1, w2, c)
            VALUES (?, ?, ?)

            ON CONFLICT(w1, w2)
            DO UPDATE SET c = c + excluded.c
            """,
            [
                (a, b, c)
                for (a, b), c in tri_ctx.items()
            ]
        )

        self.cur.executemany(
            """
            INSERT INTO quadrigram_context(
                w1, w2, w3, c
            )
            VALUES (?, ?, ?, ?)

            ON CONFLICT(w1, w2, w3)
            DO UPDATE SET c = c + excluded.c
            """,
            [
                (a, b, c, d)
                for (a, b, c), d in quad_ctx.items()
            ]
        )

        self.conn.commit()

    # =========================================================
    # STATISTICS
    # =========================================================

    def calculate_statistics(self):

        self.cur.execute(
            "SELECT COUNT(*) FROM vocab"
        )

        self.vocab_size = self.cur.fetchone()[0]

        self.cur.execute(
            "SELECT COALESCE(SUM(c), 0) FROM unigram"
        )

        self.total_tokens = self.cur.fetchone()[0]

    # =========================================================
    # ADD-K UNIGRAM
    # =========================================================

    def unigram_probability(self, w):

        count = 0

        if w != -1:

            self.cur.execute(
                "SELECT c FROM unigram WHERE w = ?",
                (w,)
            )

            result = self.cur.fetchone()

            if result:
                count = result[0]

        return (
            count + K
        ) / (
            self.total_tokens + K * self.vocab_size
        )

    # =========================================================
    # ADD-K BIGRAM
    # =========================================================

    def bigram_probability(self, w1, w2):

        count = 0

        if w1 != -1 and w2 != -1:

            self.cur.execute(
                """
                SELECT c
                FROM bigram
                WHERE w1 = ? AND w2 = ?
                """,
                (w1, w2)
            )

            result = self.cur.fetchone()

            if result:
                count = result[0]

        context = 0

        if w1 != -1:

            self.cur.execute(
                """
                SELECT c
                FROM bigram_context
                WHERE w1 = ?
                """,
                (w1,)
            )

            result = self.cur.fetchone()

            if result:
                context = result[0]

        return (
            count + K
        ) / (
            context + K * self.vocab_size
        )

    # =========================================================
    # ADD-K TRIGRAM
    # =========================================================

    def trigram_probability(
        self,
        w1,
        w2,
        w3
    ):

        count = 0

        if (
            w1 != -1
            and w2 != -1
            and w3 != -1
        ):

            self.cur.execute(
                """
                SELECT c
                FROM trigram
                WHERE
                    w1 = ?
                    AND w2 = ?
                    AND w3 = ?
                """,
                (w1, w2, w3)
            )

            result = self.cur.fetchone()

            if result:
                count = result[0]

        context = 0

        if w1 != -1 and w2 != -1:

            self.cur.execute(
                """
                SELECT c
                FROM trigram_context
                WHERE
                    w1 = ?
                    AND w2 = ?
                """,
                (w1, w2)
            )

            result = self.cur.fetchone()

            if result:
                context = result[0]

        return (
            count + K
        ) / (
            context + K * self.vocab_size
        )

    # =========================================================
    # ADD-K QUADRIGRAM
    # =========================================================

    def quadrigram_probability(
        self,
        w1,
        w2,
        w3,
        w4
    ):

        count = 0

        if (
            w1 != -1
            and w2 != -1
            and w3 != -1
            and w4 != -1
        ):

            self.cur.execute(
                """
                SELECT c
                FROM quadrigram
                WHERE
                    w1 = ?
                    AND w2 = ?
                    AND w3 = ?
                    AND w4 = ?
                """,
                (w1, w2, w3, w4)
            )

            result = self.cur.fetchone()

            if result:
                count = result[0]

        context = 0

        if (
            w1 != -1
            and w2 != -1
            and w3 != -1
        ):

            self.cur.execute(
                """
                SELECT c
                FROM quadrigram_context
                WHERE
                    w1 = ?
                    AND w2 = ?
                    AND w3 = ?
                """,
                (w1, w2, w3)
            )

            result = self.cur.fetchone()

            if result:
                context = result[0]

        return (
            count + K
        ) / (
            context + K * self.vocab_size
        )

    # =========================================================
    # CLOSE
    # =========================================================

    def close(self):
        self.conn.close()