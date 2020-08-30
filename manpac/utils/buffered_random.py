from manpac.utils import export

import numpy as np


@export
class BufferedRandom():
    """
    A PRNG that uses a buffer to store random numbers as to avoid overhead when generating a lot of numbers one at a time.

    Parameters
    -----------
    - *buffer_size*: (**int**)
        the number of numbers it can hold at one time
    """

    def __init__(self, buffer_size=50):
        self.buffer_size = buffer_size
        self.buffer = None
        self.consumed = self.buffer_size + 1

    def _refresh_(self):
        if self.consumed >= self.buffer_size:
            self.consumed = 0
            self.buffer = np.random.random((self.buffer_size))

    def uniform(self, lb=0, ub=1):
        """
        Return a random number in [lb; ub) from a uniform distribution.

        Parameters
        -----------
        - *lb*: (**float**)
            the lower bound the random number can take
        - *ub*: (**float**)
            the upper bound the random number can take

        Return
        -----------
        A random number in [lb; ub) from a uniform distribution.
        type: **float**
        """
        self._refresh_()
        out = self.buffer[self.consumed] * (ub - lb) + lb
        self.consumed += 1
        return out

    def randint(self, lb=0, ub=1):
        """
        Return a random number in [|lb; ub|] from a uniform distribution.

        Parameters
        -----------
        - *lb*: (**int**)
            the lower bound the random number can take
        - *ub*: (**int**)
            the upper bound the random number can take

        Return
        -----------
        A random number in [|lb; ub|] from a uniform distribution.
        type: **int**
        """
        out = self.uniform(lb, ub)
        return int(np.round(out))
