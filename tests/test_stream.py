import itertools

import pytest

from sicp_streams import Stream


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
    s = Stream(1, 2, 3)
    empty_stream = None
    assert s == s
    assert s != empty_stream
    assert s != 1
    assert Stream(1, 2, 3) != Stream(4, 5, 6)
    assert Stream(0, s) == Stream(0, s)
    s12 = Stream(1, 2)
    assert Stream(0) == Stream(0)
    assert s12 != s

    infinite_stream1 = Stream(1, lambda: infinite_stream1)
    infinite_stream2 = Stream(1, 1, lambda: infinite_stream2)

    assert infinite_stream1 == infinite_stream2
    assert infinite_stream1 != s
    assert Stream(0, infinite_stream1) == Stream(0, infinite_stream2)

    limit = Stream._eq_detect_limit
    assert Stream(*range(limit)) == Stream(*range(limit))
    with pytest.raises(RecursionError):
        assert Stream(*range(limit + 1)) != Stream(*range(limit + 1))

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
    assert repr(Stream(1, Stream(2, Stream(3)))) == \
           "sicp_streams.Stream(1, sicp_streams.Stream(2, sicp_streams.Stream(3, None)))"
    assert repr(Stream("1", Stream("2", Stream("3")))) == \
           "sicp_streams.Stream('1', sicp_streams.Stream('2', sicp_streams.Stream('3', None)))"
    ones = Stream(1, lambda: ones)
    assert repr(ones.tail) == 'sicp_streams.Stream(1, sicp_streams.Stream(...))'
    assert repr(Stream(ones, Stream(ones, None))) == \
           'sicp_streams.Stream' \
           '(sicp_streams.Stream(1, sicp_streams.Stream(...)), sicp_streams.Stream' \
           '(sicp_streams.Stream(1, sicp_streams.Stream(...)), None))'
    lambda_ = lambda: Stream(2, 3)
    assert repr(Stream(1, lambda_)) == "sicp_streams.Stream(1, " + repr(lambda_) + ")"


def test_none_is_instance():
    assert isinstance(None, Stream)


def test_getitem():
    assert Stream(*range(100))[99] == 99
    with pytest.raises(ValueError):
        # noinspection PyStatementEffect
        # should raise
        Stream(*range(100))[-1]
    with pytest.raises(IndexError):
        # noinspection PyStatementEffect
        # should raise
        Stream(*range(1))[2]


def test_from_iterable():
    assert Stream.from_iterable(iter([1, 2, 3, 4, 5])) == Stream(1, 2, 3, 4, 5)


def test_from_generator_function():
    @Stream.from_generator_function
    def run(x):
        yield from range(x)

    assert run(10) == Stream(*range(10))
