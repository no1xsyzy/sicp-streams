"""analog to itertools from standard library"""
import operator
from functools import partial

from stream import Stream


def smap(func, *streams):
    def resolve():
        tails = [s.tail for s in streams]
        if not all(tails):
            return None
        else:
            return smap(func, *tails)
    return Stream(func(*(s.head for s in streams)), resolve)


def szip(*streams):
    tails = [s.tail for s in streams]
    if not all(tails):
        return Stream(tuple(s.head for s in streams))
    return Stream(tuple(s.head for s in streams), partial(szip, *tails))


def sfilter(func, stream):
    while stream is not None and not func(stream.head):
        stream = stream.tail
    if stream is None:
        return None
    return Stream(stream.head, partial(sfilter, func, stream.tail))


def count(start=0, step=1):
    return Stream(start, partial(count, start + step, step))


def cycle(stream):
    first = None

    def tailfactory(stream):
        nonlocal first
        if stream is None:
            if first is None:
                return None
            else:
                return first
        s = Stream(stream.head, partial(tailfactory, stream.tail))
        if first is None:
            first = s
        return s

    return tailfactory(stream)


def repeat(obj, times=None):
    if times is None:
        s = Stream(obj, lambda: s)
        return s
    if times <= 0:
        return None
    return Stream(obj, partial(repeat, obj, times - 1))


def accumulate(stream, func=operator.add, *, initial=None):
    if stream is None:
        return Stream(initial)
    if initial is None:
        return accumulate(stream.tail, func, initial=stream.head)
    return Stream(initial, partial(accumulate, stream.tail, func, initial=func(initial, stream.head)))


def chain(*streams):
    if not streams:
        return None
    first, *streams = streams
    if first is None:
        return chain(*streams)
    if not streams:
        return first
    return Stream(first.head, partial(chain, first.tail, *streams))


def chain_from_streams(streams):
    if streams is None:
        return None
    first = streams.head
    streams = streams.tail
    if first is None:
        return chain_from_streams(streams)
    if streams is None:
        return first
    return Stream(first.head, partial(chain_from_streams, Stream(first.tail, streams)))


def compress(data, selectors):
    while data and selectors and not selectors.head:
        data, selectors = data.tail, selectors.tail
    if data is None or selectors is None:
        return None
    return Stream(data.head, partial(compress, data.tail, selectors.tail))


def dropwhile(predicate, stream):
    while stream and predicate(stream.head):
        stream = stream.tail
    return stream


def filterfalse(func, stream):
    while stream is not None and func(stream.head):
        stream = stream.tail
    if stream is None:
        return None
    return Stream(stream.head, partial(filterfalse, func, stream.tail))


def groupby(stream, key=None):
    if stream is None:
        return None

    if key is None:
        keyfunc = lambda x: x
    else:
        keyfunc = key
    del key

    def _grouper(stream, tgtkey):
        if stream is None or tgtkey != keyfunc(stream.head):
            return None
        return Stream(stream.head, partial(_grouper, stream.tail, tgtkey))

    currkey = keyfunc(stream.head)

    ng_stream = dropwhile(lambda x: currkey == keyfunc(x), stream)

    return Stream((currkey, _grouper(stream, currkey)), partial(groupby, ng_stream, keyfunc))


def sslice(stream, *args):
    s = slice(*args)
    start, stop, step = s.start or 0, s.stop or None, s.step or 1

    while stream is not None and start > 0 and (stop is None or stop > 0):
        stream = stream.tail
        start -= 1
        stop = stop - 1 if stop is not None else None
    if stream is None or (stop is not None and stop <= start):
        return None
    return Stream(stream.head, partial(sslice, stream, step, stop, step))


def starmap(func, stream):
    tail = stream.tail
    if not tail:
        return Stream(func(*stream.head))
    return Stream(func(*stream.head), partial(starmap, func, tail))


def takewhile(predicate, stream):
    if stream is None or not predicate(stream.head):
        return None
    return Stream(stream.head, partial(takewhile, predicate, stream.tail))


def tee(stream, n=2):
    """it is useless for stream since stream is not mutable. Kept for compatibility."""
    return (stream,) * n


def zip_longest(*streams, fillvalue=None):
    tails = [None if s is None else s.tail for s in streams]
    if not any(tails):
        return Stream(tuple(fillvalue if s is None else s.head for s in streams))
    return Stream(tuple(fillvalue if s is None else s.head for s in streams),
                  partial(zip_longest, *tails, fillvalue=fillvalue))


def product(*streams, repeat=1):
    streams, repeat = streams * repeat, 1
    # product() = [[]]
    if not streams:
        return Stream(())
    first, *rest = streams
    # product(first, *rest) = first >>= \f -> product(*rest) >>= \r -> [(f, *r)]
    return chain_from_streams(smap(lambda f: smap(lambda r: (f, *r), product(*rest)), first))


def permutations(stream, r=None):
    pool = tuple(stream)
    n = len(pool)
    r = r or n
    return smap(lambda indices: tuple(pool[i] for i in indices),
                sfilter(lambda indices: len(set(indices)) == r,
                        product(Stream(*range(n)), repeat=r)))


def combinations(stream, r):
    pool = tuple(stream)
    n = len(pool)
    return smap(lambda indices: tuple(pool[i] for i in indices),
                sfilter(lambda indices: sorted(indices) == list(indices),
                        permutations(Stream(*range(n)), r)))


def combinations_with_replacement(stream, r):
    pool = tuple(stream)
    n = len(pool)
    return smap(lambda indices: tuple(pool[i] for i in indices),
                sfilter(lambda indices: sorted(indices) == list(indices),
                        product(Stream(*range(n)), repeat=r)))
