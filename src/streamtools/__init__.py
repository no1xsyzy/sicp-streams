"""analog to itertools from standard library"""
import operator
from functools import partial

from sicp_streams import Stream


def smap(func, *streams):
    def resolve():
        tails = [s.tail for s in streams]
        if not all(tails):
            return None
        else:
            return smap(func, *tails)

    return Stream(func(*(s.head for s in streams)), resolve)


def szip(*streams):
    def resolve():
        tails = [s.tail for s in streams]
        if not all(tails):
            return None
        return szip(*tails)

    return Stream(tuple(s.head for s in streams), resolve)


def sfilter(func, stream):
    while stream is not None and not func(stream.head):
        stream = stream.tail
    if stream is None:
        return None
    return Stream(stream.head, lambda: sfilter(func, stream.tail))


def count(start=0, step=1):
    return Stream(start, partial(count, start + step, step))


def cycle(stream):
    first = None

    def tailfactory(st):
        nonlocal first
        if st is None:
            if first is None:
                return None
            else:
                return first
        s = Stream(st.head, lambda: tailfactory(st.tail))
        if first is None:
            first = s
        return s

    return tailfactory(stream)


def repeat(obj, times=None):
    if times is None:
        return cycle(Stream(obj, None))
    if times <= 0:
        return None
    return Stream(obj, partial(repeat, obj, times - 1))


def accumulate(stream, func=operator.add, *, initial=None):
    if stream is None:
        if initial is None:
            return None
        return Stream(initial)

    def resolve(stream, initial):
        if stream is None:
            return None
        head = func(initial, stream.head)
        return Stream(head, lambda: resolve(stream.tail, head))

    if initial is not None:
        return Stream(initial, lambda: resolve(stream, initial))
    return Stream(stream.head, lambda: resolve(stream.tail, stream.head))


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
    # streams = streams.tail
    if first is None:
        return chain_from_streams(streams.tail)
    # if streams.tail is None:
    #     return first
    return Stream(first.head, lambda: chain_from_streams(Stream(first.tail, streams.tail)))


def compress(data, selectors):
    while data and selectors and not selectors.head:
        data, selectors = data.tail, selectors.tail
    if data is None or selectors is None:
        return None
    return Stream(data.head, lambda: compress(data.tail, selectors.tail))


def dropwhile(predicate, stream):
    while stream and predicate(stream.head):
        stream = stream.tail
    return stream


def filterfalse(func, stream):
    while stream is not None and func(stream.head):
        stream = stream.tail
    if stream is None:
        return None
    return Stream(stream.head, lambda: filterfalse(func, stream.tail))


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
        return Stream(stream.head, lambda: _grouper(stream.tail, tgtkey))

    currkey = keyfunc(stream.head)

    return Stream((currkey, _grouper(stream, currkey)),
                  lambda: groupby(dropwhile(lambda x: currkey == keyfunc(x), stream), keyfunc))


def sslice(stream, *args):
    s = slice(*args)
    start, stop, step = s.start or 0, s.stop or float('+inf'), s.step or 1

    if stop <= start:
        return None
    while stream is not None and start > 0 and stop > 0:
        stream = stream.tail
        start -= 1
        stop -= 1
    if stream is None:
        return None
    return Stream(stream.head, lambda: sslice(stream, step, stop, step))


def starmap(func, stream):
    if not stream:
        return None
    return Stream(func(*stream.head), lambda: starmap(func, stream.tail))


def takewhile(predicate, stream):
    if stream is None or not predicate(stream.head):
        return None
    return Stream(stream.head, lambda: takewhile(predicate, stream.tail))


def tee(stream, n=2):
    """it is useless for stream since stream is not mutable. Kept for compatibility."""
    return (stream,) * n


def zip_longest(*streams, fillvalue=None):
    def resolve():
        tails = [None if s is None else s.tail for s in streams]
        if not any(tails):
            return None  # Stream(tuple(fillvalue if s is None else s.head for s in streams))
        return zip_longest(*tails, fillvalue=fillvalue)
    return Stream(tuple(fillvalue if s is None else s.head for s in streams),
                  resolve)


def product(*streams, repeat=1):
    streams = streams * repeat
    # product() = [[]]
    if not streams:
        return Stream(())
    first, *rest = streams
    # product(first, *rest) = first >>= \f -> product(*rest) >>= \r -> [(f, *r)]
    return chain_from_streams(smap(lambda f: smap(lambda r: (f, *r), product(*rest)), first))


def permutations(stream, r=None):
    pool = tuple(stream)
    n = len(pool)
    r = n if r is None else r
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
