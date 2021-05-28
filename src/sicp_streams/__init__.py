import functools
import threading
import typing
from functools import partial

_ST = typing.TypeVar('_ST')


class StreamMeta(type):
    def __instancecheck__(self, other):
        if other is None:
            return True
        return super().__instancecheck__(other)


class Stream(typing.Generic[_ST], metaclass=StreamMeta):
    __slots__ = ('_head', '_tail', '_tlocal')

    _eq_detect_limit: typing.ClassVar[int] = 500

    def __init__(self, head, *args):
        if args:
            *more_heads, tail = args
        else:
            more_heads = tail = None
        self._head = head
        if more_heads:
            self._tail = partial(Stream, *more_heads, tail)
        else:
            self._tail = tail
        self._tlocal = threading.local()
        self._tlocal.repr = False

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

        pointer_self = self
        pointer_other = other
        count = 0
        while True:
            if pointer_self.head != pointer_other.head:
                return False
            if pointer_self.tail is pointer_other.tail:
                return True
            if pointer_self.tail is None or pointer_other is None:
                return False
            pointer_self = pointer_self.tail
            pointer_other = pointer_other.tail
            count += 1
            if pointer_self is self and pointer_other is other:
                return True
            if count > self._eq_detect_limit:
                raise RecursionError

    def __repr__(self):
        if self._tlocal.repr:
            return f"{self.__class__.__module__}.{self.__class__.__name__}(...)"
        try:
            self._tlocal.repr = True
            return f"{self.__class__.__module__}.{self.__class__.__name__}({self._head!r}, {self._tail!r})"
        finally:
            self._tlocal.repr = False

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
