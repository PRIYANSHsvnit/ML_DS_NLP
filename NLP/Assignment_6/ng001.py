from __future__ import annotations

import math
import sqlite3
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple


SEP = "\x1f"
BOS = "<s>"
EOS = "</s>"
UNK = "<UNK>"


def history_key(history: Sequence[str]) -> str:
    return SEP.join(history)


class CountStore:
    """
    SQLite-backed storage for unigram/bigram/trigram/quadgram counts.

    This is deliberately SQLite based because a million-row Hindi corpus
    should NOT require keeping every possible quadgram in Python RAM.
    """

    def __init__(self, db_path: str = "ngram_model.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self.conn.execute("PRAGMA temp_store=MEMORY;")
        self.conn.execute("PRAGMA cache_size=-200000;")  # ~200 MB cache hint

        self._cache = OrderedDict()
        self.cache_size = 100000
        self._katz_alpha_cache = OrderedDict()
        self._katz_alpha_cache_size = 50000

        self._create_schema()
        self._load_meta()

    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def _create_schema(self) -> None:
        cur = self.conn.cursor()

        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS unigram (
                w TEXT PRIMARY KEY,
                c INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS bigram (
                w1 TEXT NOT NULL,
                w2 TEXT NOT NULL,
                c INTEGER NOT NULL,
                PRIMARY KEY (w1, w2)
            );

            CREATE TABLE IF NOT EXISTS trigram (
                w1 TEXT NOT NULL,
                w2 TEXT NOT NULL,
                w3 TEXT NOT NULL,
                c INTEGER NOT NULL,
                PRIMARY KEY (w1, w2, w3)
            );

            CREATE TABLE IF NOT EXISTS quadgram (
                w1 TEXT NOT NULL,
                w2 TEXT NOT NULL,
                w3 TEXT NOT NULL,
                w4 TEXT NOT NULL,
                c INTEGER NOT NULL,
                PRIMARY KEY (w1, w2, w3, w4)
            );

            CREATE TABLE IF NOT EXISTS history_stats (
                n INTEGER NOT NULL,
                history TEXT NOT NULL,
                total_count INTEGER NOT NULL,
                distinct_followers INTEGER NOT NULL,
                PRIMARY KEY (n, history)
            );

            CREATE TABLE IF NOT EXISTS gt_stats (
                n INTEGER NOT NULL,
                history TEXT NOT NULL,
                observed_types INTEGER NOT NULL,
                n1 INTEGER NOT NULL DEFAULT 0,
                n2 INTEGER NOT NULL DEFAULT 0,
                n3 INTEGER NOT NULL DEFAULT 0,
                n4 INTEGER NOT NULL DEFAULT 0,
                n5 INTEGER NOT NULL DEFAULT 0,
                n6 INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (n, history)
            );

            CREATE INDEX IF NOT EXISTS idx_bigram_w1 ON bigram(w1);
            CREATE INDEX IF NOT EXISTS idx_bigram_w2 ON bigram(w2);
            CREATE INDEX IF NOT EXISTS idx_trigram_w1w2 ON trigram(w1, w2);
            CREATE INDEX IF NOT EXISTS idx_trigram_w2w3 ON trigram(w2, w3);
            CREATE INDEX IF NOT EXISTS idx_quadgram_w1w2w3 ON quadgram(w1, w2, w3);
            """
        )

        self.conn.commit()

    def _load_meta(self) -> None:
        rows = self.conn.execute("SELECT key, value FROM metadata").fetchall()
        self.meta = {k: v for k, v in rows}

    def set_meta(self, key: str, value: str | int | float) -> None:
        self.conn.execute(
            """
            INSERT INTO metadata(key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """,
            (key, str(value)),
        )
        self.conn.commit()
        self.meta[key] = str(value)

    def get_meta(self, key: str, default=None):
        return self.meta.get(key, default)

    def _get_cached(self, key):
        if key in self._cache:
            value = self._cache.pop(key)
            self._cache[key] = value
            return value
        return None

    def _put_cache(self, key, value):
        self._cache[key] = value
        self._cache.move_to_end(key)
        if len(self._cache) > self.cache_size:
            self._cache.popitem(last=False)

    def clear_lookup_cache(self):
        self._cache.clear()
        self._katz_alpha_cache.clear()

    def get_unigram_count(self, word: str) -> int:
        key = ("u", word)
        cached = self._get_cached(key)
        if cached is not None:
            return cached

        row = self.conn.execute(
            "SELECT c FROM unigram WHERE w=?", (word,)
        ).fetchone()
        value = 0 if row is None else row[0]
        self._put_cache(key, value)
        return value

    def get_count(self, order: int, gram: Sequence[str]) -> int:
        gram = tuple(gram)

        if order == 1:
            return self.get_unigram_count(gram[0])

        key = ("c", order) + gram
        cached = self._get_cached(key)
        if cached is not None:
            return cached

        if order == 2:
            sql = "SELECT c FROM bigram WHERE w1=? AND w2=?"
        elif order == 3:
            sql = "SELECT c FROM trigram WHERE w1=? AND w2=? AND w3=?"
        elif order == 4:
            sql = """
                SELECT c FROM quadgram
                WHERE w1=? AND w2=? AND w3=? AND w4=?
            """
        else:
            raise ValueError("Only orders 1..4 are supported.")

        row = self.conn.execute(sql, gram).fetchone()
        value = 0 if row is None else row[0]

        self._put_cache(key, value)
        return value

    def history_stats(self, order: int, history: Sequence[str]) -> Tuple[int, int]:
        """
        Returns:
            (total token count for history, number of distinct followers)

        Here 'order' means the target n-gram order.
        """
        if order == 1:
            total = int(self.get_meta("total_tokens", "0"))
            types = self.vocab_size
            return total, types

        hk = history_key(history)
        key = ("hs", order, hk)
        cached = self._get_cached(key)
        if cached is not None:
            return cached

        row = self.conn.execute(
            """
            SELECT total_count, distinct_followers
            FROM history_stats
            WHERE n=? AND history=?
            """,
            (order, hk),
        ).fetchone()

        if row is None:
            return 0, 0

        value = (int(row[0]), int(row[1]))
        self._put_cache(key, value)
        return value

    @property
    def total_tokens(self) -> int:
        return int(self.get_meta("total_tokens", "0"))

    @property
    def vocab_size(self) -> int:
        return int(self.get_meta("vocab_size", "0"))

    def vocabulary(self) -> List[str]:
        return [r[0] for r in self.conn.execute("SELECT w FROM unigram")]

    def build_from_sentences(
        self,
        sentences: Iterable[Sequence[str]],
        commit_every: int = 10000,
        reset: bool = False,
        vocabulary: set[str] | None = None,
        unk_cutoff: int = 1,
    ) -> None:
        """
        Stream sentences into SQLite.

        Every commit_every sentences, batched INSERT/UPSERT operations are
        performed. This keeps RAM bounded.
        """
        if reset:
            self._drop_counts()
            self._create_schema()

        cur = self.conn.cursor()

        batch_u = Counter()
        batch_b = Counter()
        batch_t = Counter()
        batch_q = Counter()

        sentence_counter = 0
        token_counter = 0

        def flush():
            if not (batch_u or batch_b or batch_t or batch_q):
                return

            if batch_u:
                cur.executemany(
                    """
                    INSERT INTO unigram(w,c)
                    VALUES (?,?)
                    ON CONFLICT(w) DO UPDATE SET c=c+excluded.c
                    """,
                    batch_u.items(),
                )

            if batch_b:
                cur.executemany(
                    """
                    INSERT INTO bigram(w1,w2,c)
                    VALUES (?,?,?)
                    ON CONFLICT(w1,w2) DO UPDATE SET c=c+excluded.c
                    """,
                    [
                        (g[0], g[1], c)
                        for g, c in batch_b.items()
                    ],
                )

            if batch_t:
                cur.executemany(
                    """
                    INSERT INTO trigram(w1,w2,w3,c)
                    VALUES (?,?,?,?)
                    ON CONFLICT(w1,w2,w3) DO UPDATE SET c=c+excluded.c
                    """,
                    [
                        (g[0], g[1], g[2], c)
                        for g, c in batch_t.items()
                    ],
                )

            if batch_q:
                cur.executemany(
                    """
                    INSERT INTO quadgram(w1,w2,w3,w4,c)
                    VALUES (?,?,?,?,?)
                    ON CONFLICT(w1,w2,w3,w4) DO UPDATE SET c=c+excluded.c
                    """,
                    [
                        (g[0], g[1], g[2], g[3], c)
                        for g, c in batch_q.items()
                    ],
                )

            self.conn.commit()

            batch_u.clear()
            batch_b.clear()
            batch_t.clear()
            batch_q.clear()

        for tokens in sentences:
            tokens = list(tokens)
            if not tokens:
                continue

            if vocabulary is not None:
                tokens = [
                    tok
                    if tok in vocabulary or tok in (BOS, EOS, UNK)
                    else UNK
                    for tok in tokens
                ]

            sentence_counter += 1
            token_counter += len(tokens)

            for tok in tokens:
                batch_u[tok] += 1

            for i in range(len(tokens) - 1):
                batch_b[(tokens[i], tokens[i + 1])] += 1

            for i in range(len(tokens) - 2):
                batch_t[
                    (tokens[i], tokens[i + 1], tokens[i + 2])
                ] += 1

            for i in range(len(tokens) - 3):
                batch_q[
                    (
                        tokens[i],
                        tokens[i + 1],
                        tokens[i + 2],
                        tokens[i + 3],
                    )
                ] += 1

            if sentence_counter % commit_every == 0:
                flush()
                print(
                    f"[BUILD] processed sentences={sentence_counter:,} "
                    f"tokens={token_counter:,}"
                )

        flush()

        self.set_meta("total_tokens", token_counter)
        self.set_meta("vocab_size", self.conn.execute(
            "SELECT COUNT(*) FROM unigram"
        ).fetchone()[0])

        self.set_meta("num_sentences", sentence_counter)
        self.set_meta("max_order", 4)

        self.clear_lookup_cache()

        print("[BUILD] Creating history statistics...")
        self._build_history_stats()

        print("[BUILD] Creating Good-Turing statistics...")
        self._build_gt_stats()

        print("[BUILD] Database build complete.")

    def _drop_counts(self):
        cur = self.conn.cursor()
        for table in (
            "unigram",
            "bigram",
            "trigram",
            "quadgram",
            "history_stats",
            "gt_stats",
            "metadata",
        ):
            cur.execute(f"DELETE FROM {table}")
        self.conn.commit()

    def _build_history_stats(self):
        cur = self.conn.cursor()

        # n=2 history is w1 in bigram
        cur.execute("DELETE FROM history_stats WHERE n=2")
        cur.execute(
            """
            INSERT INTO history_stats(n,history,total_count,distinct_followers)
            SELECT 2,
                   w1,
                   SUM(c),
                   COUNT(*)
            FROM bigram
            GROUP BY w1
            """
        )
        self.conn.commit()

        # n=3 history is w1,w2 in trigram
        cur.execute("DELETE FROM history_stats WHERE n=3")
        rows = self.conn.execute(
            """
            SELECT w1, w2, SUM(c), COUNT(*)
            FROM trigram
            GROUP BY w1, w2
            """
        )

        batch = []
        for w1, w2, total, distinct in rows:
            batch.append(
                (
                    3,
                    history_key((w1, w2)),
                    int(total),
                    int(distinct),
                )
            )

            if len(batch) >= 50000:
                cur.executemany(
                    """
                    INSERT OR REPLACE INTO history_stats
                    (n,history,total_count,distinct_followers)
                    VALUES (?,?,?,?)
                    """,
                    batch,
                )
                self.conn.commit()
                batch.clear()

        if batch:
            cur.executemany(
                """
                INSERT OR REPLACE INTO history_stats
                (n,history,total_count,distinct_followers)
                VALUES (?,?,?,?)
                """,
                batch,
            )
            self.conn.commit()

        # n=4 history is w1,w2,w3 in quadgram
        cur.execute("DELETE FROM history_stats WHERE n=4")
        rows = self.conn.execute(
            """
            SELECT w1, w2, w3, SUM(c), COUNT(*)
            FROM quadgram
            GROUP BY w1, w2, w3
            """
        )

        batch = []
        for w1, w2, w3, total, distinct in rows:
            batch.append(
                (
                    4,
                    history_key((w1, w2, w3)),
                    int(total),
                    int(distinct),
                )
            )

            if len(batch) >= 50000:
                cur.executemany(
                    """
                    INSERT OR REPLACE INTO history_stats
                    (n,history,total_count,distinct_followers)
                    VALUES (?,?,?,?)
                    """,
                    batch,
                )
                self.conn.commit()
                batch.clear()

        if batch:
            cur.executemany(
                """
                INSERT OR REPLACE INTO history_stats
                (n,history,total_count,distinct_followers)
                VALUES (?,?,?,?)
                """,
                batch,
            )
            self.conn.commit()

        self.clear_lookup_cache()

    def _build_gt_stats(self, max_c: int = 6):
        """
        For each history, store N1..N6:
        Nr = number of distinct followers whose count is exactly r.

        This makes conditional Good-Turing evaluation possible without
        scanning every follower for every token.
        """
        cur = self.conn.cursor()
        cur.execute("DELETE FROM gt_stats")

        def process_order(
            n: int,
            sql: str,
        ):
            rows = self.conn.execute(sql)
            batch = []

            for row in rows:
                history_values = row[:-2]
                count_value = int(row[-2])
                freq_of_freq = int(row[-1])

                hk = history_key(history_values)

                # We initially insert one row for each frequency group.
                batch.append((n, hk, count_value, freq_of_freq))

                if len(batch) >= 50000:
                    self._upsert_gt_batch(batch)
                    batch.clear()

            if batch:
                self._upsert_gt_batch(batch)

        # Easier/safer implementation: construct rows in Python using SQL
        # grouped by history + count, then aggregate into a dictionary batch.
        for n, sql in [
            (
                2,
                """
                SELECT w1, c, COUNT(*)
                FROM bigram
                GROUP BY w1, c
                ORDER BY w1
                """,
            ),
            (
                3,
                """
                SELECT w1, w2, c, COUNT(*)
                FROM trigram
                GROUP BY w1, w2, c
                ORDER BY w1, w2
                """,
            ),
            (
                4,
                """
                SELECT w1, w2, w3, c, COUNT(*)
                FROM quadgram
                GROUP BY w1, w2, w3, c
                ORDER BY w1, w2, w3
                """,
            ),
        ]:
            aggregated = {}

            for row in self.conn.execute(sql):
                if n == 2:
                    hist = history_key((row[0],))
                    c_val = int(row[1])
                    n_c = int(row[2])
                elif n == 3:
                    hist = history_key((row[0], row[1]))
                    c_val = int(row[2])
                    n_c = int(row[3])
                else:
                    hist = history_key((row[0], row[1], row[2]))
                    c_val = int(row[3])
                    n_c = int(row[4])

                if hist not in aggregated:
                    aggregated[hist] = [0, 0, 0, 0, 0, 0, 0]

                if 1 <= c_val <= max_c:
                    aggregated[hist][c_val] = n_c

                aggregated[hist][0] += n_c

            batch = []
            for hist, values in aggregated.items():
                batch.append(
                    (
                        n,
                        hist,
                        int(values[0]),
                        int(values[1]),
                        int(values[2]),
                        int(values[3]),
                        int(values[4]),
                        int(values[5]),
                        int(values[6]),
                    )
                )

                if len(batch) >= 50000:
                    cur.executemany(
                        """
                        INSERT OR REPLACE INTO gt_stats
                        (n,history,observed_types,n1,n2,n3,n4,n5,n6)
                        VALUES (?,?,?,?,?,?,?,?,?)
                        """,
                        batch,
                    )
                    self.conn.commit()
                    batch.clear()

            if batch:
                cur.executemany(
                    """
                    INSERT OR REPLACE INTO gt_stats
                    (n,history,observed_types,n1,n2,n3,n4,n5,n6)
                    VALUES (?,?,?,?,?,?,?,?,?)
                    """,
                    batch,
                )
                self.conn.commit()

        # Unigram/global Good-Turing stats
        counts = [
            int(c)
            for (c,) in self.conn.execute(
                "SELECT c FROM unigram"
            )
        ]

        nvals = [0] * (max_c + 2)
        observed_types = len(counts)

        for c in counts:
            if 1 <= c <= max_c:
                nvals[c] += 1

        cur.execute(
            """
            INSERT OR REPLACE INTO gt_stats
            (n,history,observed_types,n1,n2,n3,n4,n5,n6)
            VALUES (1,'',?,?,?,?,?,?,?)
            """,
            (
                observed_types,
                nvals[1],
                nvals[2],
                nvals[3],
                nvals[4],
                nvals[5],
                nvals[6],
            ),
        )
        self.conn.commit()
        self.clear_lookup_cache()

    def _upsert_gt_batch(self, batch):
        # Kept for backward compatibility with older versions of this file.
        cur = self.conn.cursor()
        cur.executemany(
            """
            INSERT OR REPLACE INTO gt_stats
            (n,history,observed_types,n1,n2,n3,n4,n5,n6)
            VALUES (?,?,?,?,?,?,?,?,?)
            """,
            batch,
        )
        self.conn.commit()

    def _get_gt_stats(self, order: int, history: Sequence[str]):
        hk = "" if order == 1 else history_key(history)
        key = ("gt", order, hk)

        cached = self._get_cached(key)
        if cached is not None:
            return cached

        row = self.conn.execute(
            """
            SELECT observed_types,n1,n2,n3,n4,n5,n6
            FROM gt_stats
            WHERE n=? AND history=?
            """,
            (order, hk),
        ).fetchone()

        if row is None:
            return {
                "observed_types": 0,
                "N": {i: 0 for i in range(1, 7)},
            }

        result = {
            "observed_types": int(row[0]),
            "N": {i: int(row[i]) for i in range(1, 7)},
        }
        self._put_cache(key, result)
        return result

    def _gt_adjusted_count(self, c: int, stats, cutoff: int = 5) -> float:
        """
        Good-Turing adjusted count.

        For low counts use:
            c* = (c+1)N_{c+1}/N_c

        When the next count-of-count does not exist, fall back to the
        original count. This is intentionally conservative for sparse
        high-frequency tails.
        """
        if c <= 0:
            return 0.0

        if c > cutoff:
            return float(c)

        Nc = stats["N"].get(c, 0)
        Nc1 = stats["N"].get(c + 1, 0)

        if Nc <= 0 or Nc1 <= 0:
            # Count-of-counts estimates are undefined for sparse contexts.
            # Use a conservative half-count discount rather than silently
            # reverting to MLE (which leaves Katz with no backoff mass).
            return max(float(c) - 0.5, 0.0)

        # Raw count-of-counts estimates are noisy in sparse contexts and can
        # produce c* > c.  Katz requires a discounted count for seen events;
        # cap the estimate so observed probability mass cannot increase.
        return min(float(c), float((c + 1) * Nc1 / Nc))

    def good_turing_probability(
        self,
        word: str,
        history: Sequence[str],
        order: int,
        cutoff: int = 5,
    ) -> float:
        """
        Locally-normalized Good-Turing probability.

        For each history:
            N0 = |V| - observed_followers
            c0 = N1/N0
            Z  = sum_seen(c*) + N0*c0

        This gives a proper conditional distribution for each history.
        """
        history = tuple(history[-(order - 1):]) if order > 1 else tuple()
        stats = self._get_gt_stats(order, history)

        if order == 1:
            # Global unigram Good-Turing: adjust observed unigram counts using
            # global count-of-counts, then normalize over the model vocabulary.
            # This remains a proper distribution and avoids the old MLE shortcut.
            c = self.get_unigram_count(word)
            if c <= 0 or self.total_tokens <= 0:
                return 0.0
            total_adjusted = 0.0
            for freq in range(1, cutoff + 1):
                nfreq = stats["N"].get(freq, 0)
                if nfreq:
                    total_adjusted += nfreq * self._gt_adjusted_count(
                        freq, stats, cutoff
                    )
            high_mass = self.conn.execute(
                "SELECT COALESCE(SUM(c),0) FROM unigram WHERE c > ?", (cutoff,)
            ).fetchone()[0]
            total_adjusted += float(high_mass)
            if total_adjusted <= 0:
                return c / self.total_tokens
            adjusted = self._gt_adjusted_count(c, stats, cutoff)
            return adjusted / total_adjusted

        c = self.get_count(order, history + (word,))
        observed = stats["observed_types"]
        history_total = self.get_count(order - 1, history)
        if history_total <= 0 or observed <= 0:
            # An unseen context has no local count-of-counts table. Back off
            # to the shorter context instead of returning zero for every word.
            return self.good_turing_probability(
                word, history[1:], order - 1, cutoff=cutoff
            )
        V = self.vocab_size
        N0 = max(V - observed, 0)
        n1 = stats["N"].get(1, 0)
        # If the context has no singleton followers, Good-Turing cannot
        # estimate unseen mass reliably. Back off the entire conditional
        # distribution instead of assigning zero to every unseen continuation.
        if N0 > 0 and n1 <= 0:
            return self.good_turing_probability(
                word, history[1:], order - 1, cutoff=cutoff
            )
        c0 = (n1 / N0) if N0 > 0 else 0.0

        low_raw_mass = 0.0
        low_adjusted_mass = 0.0
        for freq in range(1, cutoff + 1):
            nfreq = stats["N"].get(freq, 0)
            if nfreq:
                low_raw_mass += freq * nfreq
                low_adjusted_mass += nfreq * self._gt_adjusted_count(
                    freq, stats, cutoff
                )
        high_raw_mass = max(float(history_total) - low_raw_mass, 0.0)
        total_adjusted = low_adjusted_mass + high_raw_mass + N0 * c0
        if total_adjusted <= 0:
            return 0.0
        adjusted = c0 if c == 0 else self._gt_adjusted_count(c, stats, cutoff)
        return adjusted / total_adjusted

    def interpolate_probability(
        self,
        word: str,
        history: Sequence[str],
        lambdas: Sequence[float],
    ) -> float:
        """
        Interpolated smoothing for order 2, 3, or 4.
        """
        max_order = len(history) + 1

        if len(lambdas) != max_order:
            raise ValueError(
                f"Expected {max_order} lambdas, got {len(lambdas)}"
            )

        # If a context was never observed, its conditional component is not a
        # distribution. Drop that component and renormalize the remaining
        # interpolation weights so the resulting distribution still sums to 1.
        components = [(self.get_count(1, (word,)) / max(self.total_tokens, 1), lambdas[0])]
        active_weight = lambdas[0]
        for n in range(2, max_order + 1):
            h = history[-(n - 1):]
            denom = self.get_count(n - 1, h)
            if denom <= 0:
                continue
            num = self.get_count(n, h + (word,))
            components.append((num / denom, lambdas[n - 1]))
            active_weight += lambdas[n - 1]

        if active_weight <= 0:
            return 0.0
        return sum(probability * weight for probability, weight in components) / active_weight

    def _gt_seen_probability(
        self,
        word: str,
        history: Sequence[str],
        order: int,
        cutoff: int = 5,
    ) -> float:
        """
        Good-Turing discounted probability for an observed n-gram.
        Used by Katz Backoff.
        """
        c = self.get_count(order, tuple(history) + (word,))
        if c <= 0:
            return 0.0

        stats = self._get_gt_stats(order, history)
        cstar = self._gt_adjusted_count(c, stats, cutoff)

        h_count = self.get_count(order - 1, history)
        if h_count <= 0:
            return 0.0

        return cstar / h_count

    def _lower_order_probability(
        self,
        word: str,
        history: Sequence[str],
        order: int,
        cutoff: int = 5,
    ) -> float:
        """
        Katz lower-order distribution.

        Base case uses Good-Turing unigram probabilities.
        Higher orders recursively use Katz.
        """
        if order == 1:
            return self.good_turing_probability(
                word, (), 1, cutoff=cutoff
            )

        return self.katz_probability(
            word,
            tuple(history[-(order - 1):]),
            order,
            cutoff=cutoff,
        )

    def _katz_alpha(
        self,
        history: Sequence[str],
        order: int,
        cutoff: int = 5,
    ) -> float:
        """
        Compute Katz's backoff alpha so the distribution is normalized.

        alpha(h) =
            remaining mass under discounted seen events
            --------------------------------------------
            lower-order mass assigned to unseen events
        """
        h = tuple(history)
        cache_key = (order, h, cutoff)

        if cache_key in self._katz_alpha_cache:
            value = self._katz_alpha_cache.pop(cache_key)
            self._katz_alpha_cache[cache_key] = value
            return value

        h_count = self.get_count(order - 1, h)

        if h_count <= 0:
            return 1.0

        if order == 2:
            rows = self.conn.execute(
                "SELECT w2,c FROM bigram WHERE w1=?", (h[0],)
            )
        elif order == 3:
            rows = self.conn.execute(
                """
                SELECT w3,c FROM trigram
                WHERE w1=? AND w2=?
                """,
                (h[0], h[1]),
            )
        elif order == 4:
            rows = self.conn.execute(
                """
                SELECT w4,c FROM quadgram
                WHERE w1=? AND w2=? AND w3=?
                """,
                (h[0], h[1], h[2]),
            )
        else:
            raise ValueError("Katz supports orders 2..4.")

        seen_lower_mass = 0.0
        seen_discounted_mass = 0.0

        for row in rows:
            w = row[0]
            c = int(row[1])

            # Lower-order history is h[1:]
            lower_hist = h[1:]

            lower_p = self._lower_order_probability(
                w,
                lower_hist,
                order - 1,
                cutoff=cutoff,
            )
            seen_lower_mass += lower_p

            cstar = self._gt_adjusted_count(
                c,
                self._get_gt_stats(order, h),
                cutoff,
            )

            seen_discounted_mass += cstar / h_count

        beta = max(1.0 - seen_discounted_mass, 0.0)
        lower_unseen_mass = max(1.0 - seen_lower_mass, 0.0)

        # If the lower-order model assigns essentially no mass to the unseen
        # continuation set, the classic ratio is numerically unstable.  In
        # that edge case, distribute the remaining mass uniformly over unseen
        # vocabulary items; katz_probability recognizes this negative sentinel.
        if lower_unseen_mass <= 1e-12:
            seen_count = self.history_stats(order, h)[1]
            unseen_count = max(self.vocab_size - seen_count, 0)
            alpha = -(beta / unseen_count) if unseen_count > 0 and beta > 0 else 0.0
        else:
            alpha = beta / lower_unseen_mass

        self._katz_alpha_cache[cache_key] = alpha
        if len(self._katz_alpha_cache) > self._katz_alpha_cache_size:
            self._katz_alpha_cache.popitem(last=False)

        return alpha

    def katz_probability(
        self,
        word: str,
        history: Sequence[str],
        order: int | None = None,
        cutoff: int = 5,
    ) -> float:
        """
        Katz Backoff:
        - observed high-order n-gram -> GT discounted probability
        - unseen -> alpha(history) * lower-order Katz probability
        """
        if order is None:
            order = len(history) + 1

        history = tuple(history[-(order - 1):])

        c = self.get_count(order, history + (word,))

        if c > 0:
            return self._gt_seen_probability(
                word, history, order, cutoff
            )

        if order == 1:
            return self.good_turing_probability(
                word, (), 1, cutoff=cutoff
            )

        alpha = self._katz_alpha(
            history, order, cutoff=cutoff
        )
        if alpha < 0.0:
            # Uniform fallback mass for the unseen vocabulary items when the
            # lower-order denominator is numerically zero.
            return -alpha

        lower = self._lower_order_probability(
            word,
            history[1:],
            order - 1,
            cutoff=cutoff,
        )

        return alpha * lower

    def stupid_backoff_score(
        self,
        word: str,
        history: Sequence[str],
        alpha: float = 0.4,
    ) -> float:
        """
        Stupid Backoff score. NOT a normalized probability.
        """
        history = tuple(history[-3:])

        # Determine available order from history length.
        for order in range(len(history) + 1, 1, -1):
            h = history[-(order - 1):]
            denom = self.get_count(order - 1, h)
            num = self.get_count(order, h + (word,))

            if denom > 0 and num > 0:
                backoff_steps = len(history) + 1 - order
                return (alpha ** backoff_steps) * (num / denom)

        unigram = self.get_unigram_count(word)

        if self.total_tokens <= 0:
            return 0.0

        return (alpha ** len(history)) * (
            unigram / self.total_tokens
        )

    def _continuation_probability(self, word: str) -> float:
        """
        Kneser-Ney continuation probability:
            # distinct predecessors of word
            --------------------------------
            # distinct bigram types
        """
        key = ("cont", word)
        cached = self._get_cached(key)
        if cached is not None:
            return cached

        row = self.conn.execute(
            "SELECT COUNT(*) FROM bigram WHERE w2=?", (word,)
        ).fetchone()
        numerator = int(row[0])

        denominator = int(
            self.conn.execute(
                "SELECT COUNT(*) FROM bigram"
            ).fetchone()[0]
        )

        p = numerator / denominator if denominator > 0 else 0.0
        self._put_cache(key, p)
        return p

    def kneser_ney_probability(
        self,
        word: str,
        history: Sequence[str],
        order: int | None = None,
        D: float = 0.75,
    ) -> float:
        """
        Interpolated absolute-discount Kneser-Ney smoothing.

        Works recursively for Bigram, Trigram and Quadgram models.
        """
        if order is None:
            order = len(history) + 1

        if order == 1:
            return self._continuation_probability(word)

        history = tuple(history[-(order - 1):])

        c = self.get_count(order, history + (word,))
        h_count, distinct_followers = self.history_stats(order, history)

        if h_count <= 0:
            return self.kneser_ney_probability(
                word,
                history[1:],
                order=order - 1,
                D=D,
            )

        first_term = max(c - D, 0.0) / h_count

        lambda_h = (
            D * distinct_followers / h_count
        )

        lower = self.kneser_ney_probability(
            word,
            history[1:],
            order=order - 1,
            D=D,
        )

        return first_term + lambda_h * lower


def sentence_probability(
    store: CountStore,
    tokens: Sequence[str],
    method: str,
    order: int,
    **kwargs,
) -> Tuple[float, int, int]:
    """
    Returns:
        log_probability,
        token_count,
        zero_count
    """
    logp = 0.0
    token_count = 0
    zero_count = 0

    for i in range(order - 1, len(tokens)):
        word = tokens[i]
        history = tuple(tokens[i - (order - 1):i])

        if method == "mle":
            if order == 1:
                p = store.get_count(1, (word,)) / max(store.total_tokens, 1)
            else:
                numerator = store.get_count(order, history + (word,))
                denominator = store.get_count(order - 1, history)
                p = numerator / denominator if denominator > 0 else 0.0
        elif method == "interpolation":
            p = store.interpolate_probability(
                word, history, kwargs["lambdas"]
            )
        elif method == "good_turing":
            p = store.good_turing_probability(
                word, history, order,
                cutoff=kwargs.get("cutoff", 5),
            )
        elif method == "katz":
            p = store.katz_probability(
                word, history, order,
                cutoff=kwargs.get("cutoff", 5),
            )
        elif method == "stupid_backoff":
            p = store.stupid_backoff_score(
                word, history,
                alpha=kwargs.get("alpha", 0.4),
            )
        elif method == "kneser_ney":
            p = store.kneser_ney_probability(
                word, history, order,
                D=kwargs.get("D", 0.75),
            )
        else:
            raise ValueError(f"Unknown method: {method}")

        token_count += 1

        if p <= 0.0 or not math.isfinite(p):
            zero_count += 1
            logp += math.log(1e-300)
        else:
            logp += math.log(p)

    return logp, token_count, zero_count
