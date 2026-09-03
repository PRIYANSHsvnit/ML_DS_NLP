from fst import FST

class Analyzer:

    def __init__(self, lexicon):
        self.lexicon = lexicon
        self.fst = FST()

    def analyze(self, word):

        # Do not convert to lowercase.
        # Uppercase letters, digits and special characters
        # should be treated as invalid.

        if not self.is_valid_word(word):
            return "Invalid Word"

        # First check possible plural forms.
        # Examples:
        # bags      -> bag + N + PL
        # foxes     -> fox + N + PL
        # watches   -> watch + N + PL
        # tries     -> try + N + PL

        possible_roots = self.find_possible_roots(word)

        for root in possible_roots:

            # Root must exist in Brown noun lexicon
            if not self.lexicon.contains(root):
                continue

            # Generate plural using FST
            generated = self.fst.generate(root, "PL")

            # Check whether generated word matches input
            if generated == word:
                return f"{root}+N+PL"

        # If it is not a valid plural, check singular.
        # Example:
        # fox -> fox + N + SG
        # bag -> bag + N + SG

        if self.lexicon.contains(word):
            return f"{word}+N+SG"

        # No valid morphological analysis exists.

        return "Invalid Word"

    def find_possible_roots(self, word):

        roots = []

        # Rule 1: S addition
        # bags -> bag
        # dogs -> dog
        # books -> book

        if word.endswith("s") and not word.endswith("ies"):

            root = word[:-1]

            if root:
                roots.append(root)

        # Rule 2: E insertion
        # foxes -> fox
        # boxes -> box
        # watches -> watch
        # dishes -> dish

        if word.endswith("es"):

            root = word[:-2]

            if root:
                roots.append(root)

        # Rule 3: Y replacement
        # tries -> try
        # cities -> city
        # babies -> baby

        if word.endswith("ies"):

            root = word[:-3] + "y"

            roots.append(root)

        return roots

    def is_valid_word(self, word):

        # Valid simplified English word:
        # one or more lowercase letters only

        if not word:
            return False

        for character in word:

            if not ('a' <= character <= 'z'):
                return False

        return True