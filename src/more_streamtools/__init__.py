from streamtools import *


def take(n, stream):
    return list(sslice(stream, n))


def prepend(value, stream):
    return Stream(value, stream)


def tabulate(function, start=0):
    return smap(function, count(start))


def tail(n, stream):
    pointers = []
    p_stream = stream
    while p_stream is not None:
        pointers.append(p_stream)
        if len(pointers) > n:
            pointers.pop(0)
        p_stream = p_stream.tail
    if pointers:
        return pointers[0]
    return None


def all_equal(stream):
    g = groupby(stream)
    return g is None or g.tail is None


def quantify(stream, pred=bool):
    p = stream
    c = 0
    while p is not None:
        c += bool(pred(p.head))
        p = p.tail
    return c


def pad_none(stream):
    return chain(stream, repeat(None))


def ncycles(stream, n):
    return chain_from_streams(repeat(stream, n))


def dotproduct(vec1, vec2):
    return sum(smap(lambda x, y: x * y, vec1, vec2))


def convolve(signal, kernel):
    kernel = tuple(kernel)[::-1]
    n = len(kernel)
    kernel = Stream(*kernel)
    signal = chain(repeat(0, n - 1), signal)

    def resolve(s):
        if s is None:
            return None
        return Stream(dotproduct(s, kernel), lambda: resolve(s.tail))

    return resolve(signal)


def flatten(stream_of_streams):
    return chain_from_streams(stream_of_streams)


def repeatfunc(func, times=None, *args):
    if times is None:
        return starmap(func, repeat(args))
    return starmap(func, repeat(args, times))


def pairwise(stream):
    if stream is None:
        return None
    return szip(stream, stream.tail)


def grouper(stream, n, fillvalue=None):
    if stream is None:
        return None
    z = []
    for _ in range(n):
        if stream is None:
            z.append(fillvalue)
        else:
            z.append(stream.head)
            stream = stream.tail
    return Stream(z, partial(grouper, stream, n, fillvalue))


def roundrobin(*streams):
    while streams and streams[0] is None:
        streams = streams[1:]
    if not streams:
        return None
    first, *streams = streams
    return Stream(first.head, lambda: roundrobin(*streams, first.tail))


def partition(predicate, stream):
    return filterfalse(predicate, stream), sfilter(predicate, stream)


@Stream.from_generator_function
def powerset(stream):
    length = len(list(stream))
    for r in range(length + 1):
        for c in combinations(stream, r):
            yield c


def unique_everseen(stream, key=None):
    if key is None:
        key = lambda x: x
    seen = set()

    def resolve(s):
        while s is not None:
            k = key(s.head)
            if k not in seen:
                break
            s = s.tail
        else:  # s is None
            return None
        seen.add(k)
        return Stream(s.head, lambda: resolve(s.tail))

    return resolve(stream)


def unique_justseen(stream, key=None):
    return smap(lambda x: x[1].head, groupby(stream, key))


def iter_except(func, exception, first=None):
    try:
        if first is not None:
            v = first()
        else:
            v = func()
        return Stream(v, lambda: iter_except(func, exception))
    except exception:
        return None


def first_true(stream, default=False, predicate=None):
    if predicate is None:
        predicate = bool
    n = sfilter(predicate, stream)
    if n is None:
        return default
    else:
        return n.head
