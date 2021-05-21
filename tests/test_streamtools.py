import operator

import streamtools
from stream import Stream


def test_smap():
    mapped = streamtools.smap(lambda x, y: x + y, Stream(1, 2, 3), Stream(4, 5, 6))
    direct = Stream(5, 7, 9)
    assert mapped.head == 5
    assert mapped.tail.head == 7
    assert mapped.tail.tail.head == 9
    assert mapped.tail.tail.tail is None
    assert mapped == direct


def test_szip():
    assert streamtools.szip(Stream(1, 2, 3), Stream(4, 5, 6)) == Stream((1, 4), (2, 5), (3, 6))


def test_sfilter():
    assert streamtools.sfilter(lambda x: x % 2 == 0, Stream.from_iterable(range(10))) == Stream(0, 2, 4, 6, 8)


def test_count():
    s = streamtools.count()
    assert s.head == 0
    assert s.tail.head == 1
    assert s.tail.tail.head == 2


def test_cycle():
    s = streamtools.cycle(Stream(1, 2, 3))
    assert s.head == 1
    assert s.tail.head == 2
    assert s.tail.tail.head == 3
    assert s.tail.tail.tail is s

    assert streamtools.cycle(None) is None


def test_repeat():
    obj = object()
    infinite = streamtools.repeat(obj)
    assert infinite.head is obj
    assert infinite.tail is infinite

    r3 = streamtools.repeat(obj, 3)
    assert r3.head is obj
    assert r3.tail.head is obj
    assert r3.tail.tail.head is obj
    assert r3.tail.tail.tail is None


def test_accumulate():
    assert streamtools.accumulate(Stream(1, 2, 3, 4, 5)) == Stream(1, 3, 6, 10, 15)
    assert streamtools.accumulate(Stream(1, 2, 3, 4, 5), initial=100) == Stream(100, 101, 103, 106, 110, 115)
    assert streamtools.accumulate(Stream(1, 2, 3, 4, 5), operator.mul) == Stream(1, 2, 6, 24, 120)


def test_chain():
    s1t3 = Stream(1, 2, 3)
    s4t6 = Stream(4, 5, 6)
    s1t6 = Stream(1, 2, 3, 4, 5, 6)
    assert streamtools.chain(s1t3, s4t6) == s1t6
    assert streamtools.chain(s1t3, s4t6).tail.tail.tail is s4t6


def test_chain_from_streams():
    s1t3 = Stream(1, 2, 3)
    s4t6 = Stream(4, 5, 6)
    s1t6 = Stream(1, 2, 3, 4, 5, 6)
    assert streamtools.chain_from_streams(Stream(s1t3, s4t6, None)) == s1t6
    assert streamtools.chain_from_streams(Stream(s1t3, s4t6, None)).tail.tail.tail is s4t6


def test_compress():
    assert streamtools.compress(Stream(*"ABCDE"), Stream(1, 0, 1, 0, 1)) == Stream(*"ACE")
    assert streamtools.compress(Stream(*"ABCDE"), Stream(1)) == Stream("A")
    assert streamtools.compress(Stream("A"), Stream(1, 1)) == Stream("A")
    assert streamtools.compress(Stream("A"), Stream(0, 1)) is None


def test_dropwhile():
    assert streamtools.dropwhile(lambda x: x < 5, Stream(1, 4, 6, 4, 1)) == Stream(6, 4, 1)


def test_filterfalse():
    assert streamtools.filterfalse(lambda x: x % 2, Stream(*range(10))) == Stream(0, 2, 4, 6, 8)


def test_groupby():
    grouped = streamtools.groupby(Stream(*"AAAABBBCCDAABBB"))
    assert streamtools.smap(lambda x: x[0], grouped) == Stream(*"ABCDAB")
    assert streamtools.smap(lambda x: x[1], grouped) == Stream(
        Stream(*"AAAA"),
        Stream(*"BBB"),
        Stream(*"CC"),
        Stream(*"D"),
        Stream(*"AA"),
        Stream(*"BBB"),
        None
    )


def test_sslice():
    s = Stream(*"ABCDEFG")
    assert streamtools.sslice(s, 2) == Stream(*"AB")
    assert streamtools.sslice(s, 2, 4) == Stream(*"CD")
    assert streamtools.sslice(s, 2, None) == Stream(*"CDEFG")
    assert streamtools.sslice(s, 0, None, 2) == Stream(*"ACEG")


def test_starmap():
    assert streamtools.starmap(pow, Stream((2, 5), (3, 2), (10, 3))) == Stream(32, 9, 1000)


def test_takewhile():
    assert streamtools.takewhile(lambda x: x < 5, Stream(1, 4, 6, 4, 1)) == Stream(1, 4)


def test_tee():
    s = Stream(1, 2, 3)
    teed = streamtools.tee(s)
    assert teed[0] is teed[1] is s


def test_zip_longest():
    assert streamtools.zip_longest(Stream(*'ABCD'), Stream(*'xy'),
                                   fillvalue='-') == Stream(
        ('A', 'x'), ('B', 'y'), ('C', '-'), ('D', '-'))


def test_product():
    assert streamtools.product(Stream(*"ABCD"), Stream(*"xy")) == Stream(
        ('A', 'x'),
        ('A', 'y'),
        ('B', 'x'),
        ('B', 'y'),
        ('C', 'x'),
        ('C', 'y'),
        ('D', 'x'),
        ('D', 'y'),
    )
    assert streamtools.product(Stream(*range(2)), repeat=3) == Stream(
        (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1),
        (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1),
    )


def test_permutations():
    assert streamtools.permutations(Stream(*"ABCD"), 2) == Stream(
        ('A', 'B'),
        ('A', 'C'),
        ('A', 'D'),
        ('B', 'A'),
        ('B', 'C'),
        ('B', 'D'),
        ('C', 'A'),
        ('C', 'B'),
        ('C', 'D'),
        ('D', 'A'),
        ('D', 'B'),
        ('D', 'C'),
    )

    assert streamtools.permutations(Stream(*range(3))) == Stream(
        (0, 1, 2),
        (0, 2, 1),
        (1, 0, 2),
        (1, 2, 0),
        (2, 0, 1),
        (2, 1, 0),
    )


def test_combinations():
    assert streamtools.combinations(Stream(*"ABCD"), 2) == Stream(
        ("A", "B"),
        ("A", "C"),
        ("A", "D"),
        ("B", "C"),
        ("B", "D"),
        ("C", "D"),
    )

    assert streamtools.combinations(Stream(*range(4)), 3) == Stream(
        (0, 1, 2),
        (0, 1, 3),
        (0, 2, 3),
        (1, 2, 3),
    )


def test_combinations_with_replacement():
    assert streamtools.combinations_with_replacement(Stream(*"ABC"), 2) == Stream(
        ("A", "A"),
        ("A", "B"),
        ("A", "C"),
        ("B", "B"),
        ("B", "C"),
        ("C", "C"),
    )
