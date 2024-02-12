from collections import OrderedDict
from concurrent.futures import Future

from flask_executor.helpers import InstanceProxy


class FutureCollection:
    """A FutureCollection is an object to store and interact with
    :class:`concurrent.futures.Future` objects. It provides access to all
    attributes and methods of a Future by proxying attribute calls to the
    stored Future object.

    To access the methods of a Future from a FutureCollection instance, include
    a valid ``future_key`` value as the first argument of the method call. To
    access attributes, call them as though they were a method with
    ``future_key`` as the sole argument. If ``future_key`` does not exist, the
    call will always return None. If ``future_key`` does exist but the
    referenced Future does not contain the requested attribute an
    :exc:`AttributeError` will be raised.

    To prevent memory exhaustion a FutureCollection instance can be bounded by
    number of items using the ``max_length`` parameter. As a best practice,
    Futures should be popped once they are ready for use, with the proxied
    attribute form used to determine whether a Future is ready to be used or
    discarded.

    :param max_length: Maximum number of Futures to store. Oldest Futures are
    discarded first.

    """

    def __init__(self, max_length=50):
        self.max_length = max_length
        self._futures = OrderedDict()

    def __contains__(self, future):
        return future in self._futures.values()

    def __len__(self):
        return len(self._futures)

    def __getattr__(self, attr):
        # Call any valid Future method or attribute
        def _future_attr(future_key, *args, **kwargs):
            if future_key not in self._futures:
                return None
            future_attr = getattr(self._futures[future_key], attr)
            if callable(future_attr):
                return future_attr(*args, **kwargs)
            return future_attr

        return _future_attr

    def _check_limits(self):
        if self.max_length is not None:
            while len(self._futures) > self.max_length:
                self._futures.popitem(last=False)

    def add(self, future_key, future):
        """Add a new Future. If ``max_length`` limit was defined for the
        FutureCollection, old Futures may be dropped to respect this limit.

        :param future_key: Key for the Future to be added.
        :param future: Future to be added.
        """
        if future_key in self._futures:
            raise ValueError("future_key {} already exists".format(future_key))
        self._futures[future_key] = future
        self._check_limits()

    def pop(self, future_key):
        """Return a Future and remove it from the collection. Futures that are
        ready to be used should always be popped so they do not continue to
        consume memory.

        Returns ``None`` if the key doesn't exist.

        :param future_key: Key for the Future to be returned.
        """
        return self._futures.pop(future_key, None)


class FutureProxy(InstanceProxy, Future):
    """A FutureProxy is an instance proxy that wraps an instance of
    :class:`concurrent.futures.Future`. Since an executor can't be made to
    return a subclassed Future object, this proxy class is used to override
    instance behaviours whilst providing an agnostic method of accessing
    the original methods and attributes.
    :param future: An instance of :class:`~concurrent.futures.Future` that
                   the proxy will provide access to.
    :param executor: An instance of :class:`flask_executor.Executor` which
                     will be used to provide access to Flask context features.
    """

    def __init__(self, future, executor):
        self._self = future
        self._executor = executor

    def add_done_callback(self, fn):
        fn = self._executor._prepare_fn(fn, force_copy=True)
        return self._self.add_done_callback(fn)

    def __eq__(self, obj):
        return self._self == obj

    def __hash__(self):
        return self._self.__hash__()
