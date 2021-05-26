"""Well-known streams"""

from functools import partial

import streamtools
from stream import Stream


def _sieve(stream):
    if stream is None:
        return None

    return Stream(stream.head, partial(_sieve, streamtools.sfilter(lambda x: x % stream.head != 0, stream.tail)))


primes = _sieve(streamtools.count(2))

ones = Stream(1, lambda: ones)

integers = Stream(1, lambda: streamtools.smap(lambda x, y: x + y, ones, integers))

fibs = Stream(0, 1, lambda: streamtools.smap(lambda x, y: x + y, fibs.tail, fibs))

factorials = Stream(1, lambda: streamtools.smap(lambda x, y: x * y,
                                                factorials,
                                                streamtools.count(2)))


def _prime2p(n):
    for carps in primes:
        if carps * carps > n:
            return True
        if n % carps == 0:
            return False


primes2 = Stream(2, lambda: streamtools.sfilter(_prime2p, streamtools.count(3)))


@Stream.from_generator_function
def pi_summands(x):
    sign = 1
    while True:
        yield sign / x
        sign = -sign
        x += 2


pi_stream = streamtools.smap(lambda x: x * 4, streamtools.accumulate(pi_summands(1)))


def euler_transform(s):
    s0 = s[0]
    s1 = s[1]
    s2 = s[2]

    return Stream(s2 - (s2 - s1) ** 2 / (s0 - 2 * s1 + s2),
                  lambda: euler_transform(s.tail))


def make_tableau(transform, s):
    return Stream(s, lambda: make_tableau(transform, transform(s)))


def accelerated_sequence(transform, s):
    return streamtools.smap(lambda st: st.head,
                            make_tableau(transform, s))


accelerated_pi_stream = accelerated_sequence(euler_transform, pi_stream)
