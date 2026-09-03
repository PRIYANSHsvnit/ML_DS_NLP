import sys
from pathlib import Path

# Add Assignment_3 directory to Python's module search path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from DFA.dfa import DFA


class Lexicon:

    def __init__(self, filename="brown_nouns.txt"):

        self.nouns = set()

        # Use the DFA to filter the Brown corpus
        self.dfa = DFA()

        self.load(filename)

    def load(self, filename):

        try:

            with open(filename, "r", encoding="utf-8") as file:

                for line in file:

                    word = line.strip()

                    # Only accept words recognized by the DFA
                    if word and self.dfa.accepts(word):

                        self.nouns.add(word)

        except FileNotFoundError:

            print(f"ERROR: {filename} not found.")
            print("Make sure brown_nouns.txt is in the FST folder.")

    def contains(self, word):

        return word in self.nouns

    def size(self):

        return len(self.nouns)