# Streams

Honor [SICP 3.5 Streams](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book-Z-H-24.html). It shows a
way to see "changing" data differently.

## Introduction

Iterators actually irrecoverably consumes the data in it. This is not acceptable for (not pure but Lisp-like) functional
programming. This package is built for solve this.

Stream is designed to be immutable, but not enforced by codes. Prevent doing anything with `s._head` or `s._tail`.

## Usage (all codes are complete)

```python
## Importing and Constructing a Stream
from sicp_streams import Stream

s = Stream("axolotl", "barnacle", "coral")

# Equivalently, use another stream as last element means "rest"
# s = Stream("axolotl", Stream("barnacle", Stream("coral", None)))

# Equivalently, use a callable as last element also means "rest", and will not be called until it is necessary
# s = Stream("axolotl", lambda: Stream("barnacle", lambda: Stream("coral", lambda: None)))

# Therefore, it is possible to construct a stream that never ends
ones = Stream(1, lambda: ones)

## Get Data from It
assert s.head == "axolotl"
assert s.tail.head == "barnacle"
assert s.tail.tail.head == "coral"
assert s.tail.tail.tail is None  # end of stream is None

## Get Data by subscripting
assert (s[0], s[1], s[2]) == ("axolotl", "barnacle", "coral")

## Turn into an Iterator
it = iter(s)
assert next(it) == "axolotl"
assert next(it) == "barnacle"
assert next(it) == "coral"

## Construct from an iterable
Stream.from_iterable([1, 2, 3])


## Construct from generator function
@Stream.from_generator_function
def counts(n):
    while True:
        yield n
        n += 1


integers = counts(1)
```

## Toolbox Analog to `itertools` and Iterator-related Built-in Functions

```python
from sicp_streams import Stream
import streamtools

# some of them have different name (for obvious but unnecessary reason)
# map -> smap
streamtools.smap(lambda x: x + 1, Stream(1, 2, 3))
# filter -> sfilter
streamtools.sfilter(lambda x: x % 2 == 0, Stream(1, 2, 3))
# zip -> szip
streamtools.szip(Stream(1, 2, 3), Stream(4, 5, 6))
# islice -> sslice
streamtools.sslice(Stream(1, 2, 3, 4, 5), 2, 4)
```

## Demo, reimplementing SICP 3.5 (Not all of it)

```python
import streamdemo
```
