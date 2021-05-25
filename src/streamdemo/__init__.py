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
