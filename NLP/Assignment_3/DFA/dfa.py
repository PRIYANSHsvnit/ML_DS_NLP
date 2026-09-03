class DFA:
    """
    DFA for simplified English words.

    Valid word:
        - Starts with a lowercase letter
        - Followed by zero or more lowercase letters

    States:
        q0 = Start state
        q1 = Accepting state
        qd = Dead state
    """

    def __init__(self):

        self.start_state = "q0"
        self.accept_state = "q1"
        self.dead_state = "qd"

    def transition(self, state, symbol):

        # q0: Start state

        if state == "q0":

            if 'a' <= symbol <= 'z':
                return "q1"

            return "qd"

        # q1: Accepting state

        elif state == "q1":

            if 'a' <= symbol <= 'z':
                return "q1"

            return "qd"

        # qd: Dead state

        elif state == "qd":

            return "qd"

        return "qd"

    def accepts(self, word):

        state = self.start_state

        for symbol in word:

            state = self.transition(state, symbol)

        return state == self.accept_state