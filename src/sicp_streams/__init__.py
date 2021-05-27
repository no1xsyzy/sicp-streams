import functools
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
        if self is other:
            return True
        if other is None:
            return False
        if not isinstance(other, Stream):
            return NotImplemented

        if self.head != other.head:
            return False
        return self.tail == other.tail

    def __repr__(self):
        resolved_so_far = []
        pivot = self
        resolved_so_far.append(pivot.head)
        while isinstance(pivot._tail, Stream) and pivot._tail is not None:
            pivot = pivot._tail
            resolved_so_far.append(pivot.head)
        if pivot is not None:
            resolved_so_far.append(pivot._tail)
        return self.__class__.__module__ + "." + self.__class__.__name__ + repr(tuple(resolved_so_far))

    def __getitem__(self, item):
        if item < 0:
            raise ValueError

        pointer = self
        while pointer.tail is not None and item > 0:
            pointer = pointer.tail
            item -= 1
        if item == 0:
            return pointer.head
        elif pointer.tail is None:
            raise IndexError("stream index out of range")

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

    @classmethod
    def from_generator_function(
            cls, generator_function: typing.Callable[..., typing.Iterable[_ST]]
    ) -> 'typing.Callable[..., typing.Union[Stream[_ST], None]]':
        @functools.wraps(generator_function)
        def wrapped(*args, **kwargs):
            generator = generator_function(*args, **kwargs)
            return cls.from_iterable(generator)

        return wrapped
