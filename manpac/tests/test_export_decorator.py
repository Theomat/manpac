from manpac.utils import export

import sys


@export
def random_fun1():
    return 3


def random_fun2():
    return 3


@export
class RandomClass1():
    pass


class RandomClass2():
    pass


def is_exported(fn):
    mod = sys.modules[fn.__module__]
    if hasattr(mod, '__all__'):
        name = fn.__name__
        all_ = mod.__all__
        return name in all_
    else:
        return False


def test_function():
    assert is_exported(random_fun1)
    assert not is_exported(random_fun2)


def test_class():
    assert is_exported(RandomClass1)
    assert not is_exported(RandomClass2)
