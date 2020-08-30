from manpac.utils.buffered_random import BufferedRandom


import numpy as np


def test_uniform():
    rand = BufferedRandom()

    for i in range(100):
        a = np.random.random(1)[0] * 1000 - 500
        b = np.random.random(1)[0] * 500 + a
        for j in range(1000):
            x = rand.uniform(a, b)
            assert a <= x
            assert b > x


def test_randint():
    rand = BufferedRandom()

    for i in range(100):
        a = int(np.random.random(1)[0] * 1000 - 500)
        b = int(np.random.random(1)[0] * 500 + a)
        for j in range(1000):
            x = rand.randint(a, b)
            assert a <= x
            assert b >= x
