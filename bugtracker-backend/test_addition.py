# test_sample.py
def add(a, b):
    return a + b


def test_add_success():
    assert add(2, 3) == 5


def test_add_failure():
    assert add(2, 3) == 6  # This will fail
