from more_streamtools import *


def test_take():
    assert take(2, Stream(*range(5))) == [0, 1]


def test_prepend():
    assert prepend("value", Stream(*range(5))) == Stream("value", 0, 1, 2, 3, 4)


def test_tabulate():
    assert tabulate(lambda x: x ** 2)[3] == 9
    assert tabulate(lambda x: x, 5)[0] == 5


def test_tail():
    assert tail(3, Stream(*"ABCDEFG")) == Stream(*"EFG")
    assert tail(0, Stream(*"ABCDEFG")) is None


def test_all_equal():
    assert all_equal(Stream(1, 1, 1))
    assert all_equal(None)
    assert not all_equal(Stream(1, 2, 3))


def test_quantify():
    assert quantify(Stream(1, 0, 1, 0, 1)) == 3
    assert quantify(Stream(1, 2, 3, 4, 5), lambda x: x % 2 == 0) == 2


def test_pad_none():
    assert pad_none(Stream(1)) == Stream(1, repeat(None))


def test_ncycles():
    assert ncycles(Stream(1, 2, 3), 3) == Stream(1, 2, 3, 1, 2, 3, 1, 2, 3)


def test_dotproduct():
    assert dotproduct(Stream(1, 2, 3), Stream(4, 5, 6)) == 32


def test_convolve():
    convolution = convolve(Stream(1, 2, 3, 4, 5), [0.25] * 4)
    assert convolution == Stream(0.25, 0.75, 1.5, 2.5, 3.5, 3, 2.25, 1.25)


def test_flatten():
    assert flatten(Stream(Stream(1, 2, 3), Stream(4, 5, 6), None)) == Stream(1, 2, 3, 4, 5, 6)


def test_repeatfunc():
    assert repeatfunc(lambda: 0, 10) == repeat(0, 10)
    assert repeatfunc(lambda: 0)[100] == 0


def test_pairwise():
    assert pairwise(None) is None
    assert pairwise(Stream(1, 2, 3)) == Stream((1, 2), (2, 3))


def test_grouper():
    assert grouper(Stream(*"ABCDEFG"), 3, "x") == Stream([*"ABC"], [*"DEF"], [*"Gxx"])


def test_roundrobin():
    assert roundrobin(Stream(*"ABC"), Stream("D"), Stream(*"EF")) == Stream(*"ADEBFC")


def test_partition():
    assert partition(lambda x: x % 2, Stream(*range(10))) == (Stream(*range(0, 10, 2)), Stream(*range(1, 10, 2)))


def test_powerset():
    assert powerset(Stream(1, 2, 3)) == Stream((), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3))


def test_unique_everseen():
    assert unique_everseen(Stream(*"AAAABBBCCDAABBB")) == Stream(*"ABCD")
    assert unique_everseen(Stream(*"ABBCcAD"), str.lower) == Stream(*"ABCD")


def test_unique_justseen():
    assert unique_justseen(Stream(*"AAAABBBCCDAABBB")) == Stream(*"ABCDAB")
    assert unique_justseen(Stream(*"ABBCcAD"), str.lower) == Stream(*"ABCAD")


def test_iter_except():
    lst = [1, 2, 3]
    assert iter_except(lst.pop, IndexError, lambda: 4) == Stream(4, 3, 2, 1)


def test_first_true():
    assert first_true(Stream(0, False, 9)) == 9
    assert first_true(Stream(1, 5), 9, lambda x: x > 3) == 5
    assert first_true(Stream(1, 5), 9, lambda x: x > 7) == 9
