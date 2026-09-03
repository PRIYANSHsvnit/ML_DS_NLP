from fst import FST


class Generator:

    def __init__(self, lexicon):

        self.lexicon = lexicon
        self.fst = FST()

    def generate(self, root, number):

        # Root must already be a valid lowercase word
        # from the Brown noun lexicon.
        if not self.lexicon.contains(root):
            return None

        # Generate surface form using the FST
        return self.fst.generate(root, number)

    def generate_analysis(self, root, number):

        word = self.generate(root, number)

        if word is None:
            return "Invalid Word"

        return f"{word} = {root}+N+{number}"