class FST:
    """
    Finite State Transducer for regular noun morphology.

    Morphological representation:

        root + N + SG
        root + N + PL

    Rules:

        1. S addition
           bag -> bags
           dog -> dogs

        2. E insertion
           fox -> foxes
           watch -> watches
           box -> boxes
           dish -> dishes

        3. Y replacement
           try -> tries
           city -> cities
           baby -> babies
    """

    # FST states

    NORMAL = "NORMAL"
    SPECIAL = "SPECIAL"
    Y_ENDING = "Y_ENDING"

    # Determine the morphological state of the root

    def get_state(self, root):

        # SPECIAL state
        #
        # Roots ending in:
        # s, z, x, ch, sh
        #
        # These require "es" in plural.

        if root.endswith(("s", "z", "x", "ch", "sh")):
            return self.SPECIAL

        # Y_ENDING state
        # consonant + y
        # try -> tries
        # city -> cities

        if root.endswith("y") and len(root) >= 2:

            previous = root[-2]

            if previous not in "aeiou":
                return self.Y_ENDING

        # NORMAL state
        # Regular nouns take "s".

        return self.NORMAL

    # Generate surface form

    def generate(self, root, number):

        """
        Generate a surface word from:

            root + N + SG
            root + N + PL

        Returns:
            generated word
            or None for invalid number
        """

        state = self.get_state(root)

        # Singular
        # root + N + SG -> root

        if number == "SG":
            return root

        # Plural

        if number == "PL":

            # S addition
            if state == self.NORMAL:
                return root + "s"

            # E insertion
            elif state == self.SPECIAL:
                return root + "es"

            # Y replacement
            elif state == self.Y_ENDING:
                return root[:-1] + "ies"

        # Invalid morphological number
        return None