import typing
from functools import partial

_ST = typing.TypeVar('_ST')


class StreamMeta(type):
    def __instancecheck__(self, other):
        if other is None:
            return True
        return super().__instancecheck__(other)


class Stream(typing.Generic[_ST], metaclass=StreamMeta):
    __slots__ = ('_head', '_tail')

    def __init__(self, head, *args):
        if args:
            *more_heads, tail = args
        else:
            more_heads = tail = None
        self._head = head
        if more_heads:
            self._tail = Stream(*more_heads, tail)
        else:
            self._tail = tail

    @property
    def head(self) -> _ST:
        return self._head

    @property
    def tail(self) -> 'typing.Union[Stream[_ST], None]':
        if callable(self._tail):
            self._tail = self._tail()
        if not (self._tail is None or isinstance(self._tail, Stream)):
            self._tail = Stream(self._tail)
        return self._tail

    def __iter__(self) -> typing.Iterable[_ST]:
        y = self
        while y is not None:
            yield y.head
            y = y.tail

    def __eq__(self, other: 'typing.Union[Stream[_ST], None]'):
        """use with caution: it will try to drain the stream.
        If both streams are long enough, it will raise RecursionError"""
        if other is None:
            return False
        if not isinstance(other, Stream):
            return NotImplemented
        try:
            return self.head == other.head and self.tail == other.tail
        except RecursionError:
            return NotImplemented

    def __repr__(self):
        resolved_so_far = []
        pivot = self
        resolved_so_far.append(pivot.head)
        while isinstance(pivot._tail, Stream):
            pivot = pivot._tail
            resolved_so_far.append(pivot.head)
        if pivot is not None:
            resolved_so_far.append(pivot._tail)
        return self.__class__.__module__+"."+self.__class__.__name__+repr(tuple(resolved_so_far))

    @classmethod
    def from_iterable(cls, iterable: typing.Iterable[_ST]) -> 'typing.Union[Stream[_ST], None]':
        """should consume the iterable"""
        it = iter(iterable)
        try:
            n = next(it)
        except StopIteration:
            return None
        else:
            return cls(n, partial(cls.from_iterable, it))
