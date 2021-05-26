import itertools

import pytest
from stream import Stream


def test_new_stream():
    s = Stream(1, lambda: 2)
    assert s.head == 1
    assert s.tail.head == 2
    assert s.tail.tail is None


def test_stream_class_multi():
    s = Stream(1, 2, 3)
    assert s.head == 1
    assert s.tail.head == 2
    assert s.tail.tail.head == 3
    assert s.tail.tail.tail is None


def test_stream_delayed_evaluation():
    class TempException(Exception):
        pass

    def fails():
        raise TempException

    s = Stream(0, fails)

    assert s.head == 0

    with pytest.raises(TempException):
        print(s.tail)


def test_stream_from_list():
    s = Stream.from_iterable([1, 2, 3])
    assert s.head == 1
    assert s.tail.head == 2
    assert s.tail.tail.head == 3


def test_list_from_stream():
    s = Stream.from_iterable([1, 2, 3])
    assert list(s) == [1, 2, 3]


def test_equivalence():
    for a, b in itertools.combinations([
        Stream(1, 2, 3),
        Stream(1, Stream(2, 3)),
        Stream(1, Stream(2, Stream(3))),
        Stream(1, Stream(2, Stream(3, None))),
        Stream.from_iterable([1, 2, 3]),
        Stream.from_iterable(range(1, 4)),
    ], 2):
        assert a == b


def test_repr():
    assert repr(Stream(1, 2, 3)) == "stream.Stream(1, 2, 3)"
    lambda_ = lambda: Stream(2, 3)
    assert repr(Stream(1, lambda_)) == "stream.Stream(1, " + repr(lambda_) + ")"


def test_none_is_instance():
    assert isinstance(None, Stream)


def test_getitem():
    assert Stream(*range(100))[99] == 99


def test_from_iterable():
    assert Stream.from_iterable(iter([1, 2, 3, 4, 5])) == Stream(1, 2, 3, 4, 5)
