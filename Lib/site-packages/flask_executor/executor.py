import concurrent.futures
import contextvars
import copy
import re

from flask import copy_current_request_context, current_app, g

from flask_executor.futures import FutureCollection, FutureProxy
from flask_executor.helpers import InstanceProxy, str2bool


def get_current_app_context():
    try:
        from flask.globals import _cv_app
        return _cv_app.get(None)
    except ImportError:
        from flask.globals import _app_ctx_stack
        return _app_ctx_stack.top


def push_app_context(fn):
    app = current_app._get_current_object()
    _g = copy.copy(g)

    def wrapper(*args, **kwargs):
        with app.app_context():
            ctx = get_current_app_context()
            ctx.g = _g
            return fn(*args, **kwargs)

    return wrapper


def propagate_exceptions_callback(future):
    exc = future.exception()
    if exc:
        raise exc


class ExecutorJob:
    """Wraps a function with an executor so to allow the wrapped function to
    submit itself directly to the executor."""

    def __init__(self, executor, fn):
        self.executor = executor
        self.fn = fn

    def submit(self, *args, **kwargs):
        future = self.executor.submit(self.fn, *args, **kwargs)
        return future

    def submit_stored(self, future_key, *args, **kwargs):
        future = self.executor.submit_stored(future_key, self.fn, *args, **kwargs)
        return future

    def map(self, *iterables, **kwargs):
        results = self.executor.map(self.fn, *iterables, **kwargs)
        return results


class Executor(InstanceProxy, concurrent.futures._base.Executor):
    """An executor interface for :py:mod:`concurrent.futures` designed for
    working with Flask applications.

    :param app: A Flask application instance.
    :param name: An optional name for the executor. This can be used to
                 configure multiple executors. Named executors will look for
                 environment variables prefixed with the name in uppercase,
                 e.g. ``CUSTOM_EXECUTOR_TYPE``.
    """

    def __init__(self, app=None, name=''):
        self.app = app
        self._default_done_callbacks = []
        self.futures = FutureCollection()
        if re.match(r'^(\w+)?$', name) is None:
            raise ValueError(
                "Executor names may only contain letters, numbers or underscores"
            )
        self.name = name
        prefix = name.upper() + '_' if name else ''
        self.EXECUTOR_TYPE = prefix + 'EXECUTOR_TYPE'
        self.EXECUTOR_MAX_WORKERS = prefix + 'EXECUTOR_MAX_WORKERS'
        self.EXECUTOR_FUTURES_MAX_LENGTH = prefix + 'EXECUTOR_FUTURES_MAX_LENGTH'
        self.EXECUTOR_PROPAGATE_EXCEPTIONS = prefix + 'EXECUTOR_PROPAGATE_EXCEPTIONS'
        self.EXECUTOR_PUSH_APP_CONTEXT = prefix + 'EXECUTOR_PUSH_APP_CONTEXT'

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialise application. This will also intialise the configured
        executor type:

            * :class:`concurrent.futures.ThreadPoolExecutor`
            * :class:`concurrent.futures.ProcessPoolExecutor`
        """
        app.config.setdefault(self.EXECUTOR_TYPE, 'thread')
        app.config.setdefault(self.EXECUTOR_PUSH_APP_CONTEXT, True)
        futures_max_length = app.config.setdefault(self.EXECUTOR_FUTURES_MAX_LENGTH, None)
        propagate_exceptions = app.config.setdefault(self.EXECUTOR_PROPAGATE_EXCEPTIONS, False)
        if futures_max_length is not None:
            self.futures.max_length = int(futures_max_length)
        if str2bool(propagate_exceptions):
            self.add_default_done_callback(propagate_exceptions_callback)
        self._self = self._make_executor(app)
        app.extensions[self.name + 'executor'] = self

    def _make_executor(self, app):
        executor_max_workers = app.config.setdefault(self.EXECUTOR_MAX_WORKERS, None)
        if executor_max_workers is not None:
            executor_max_workers = int(executor_max_workers)
        executor_type = app.config[self.EXECUTOR_TYPE]
        if executor_type == 'thread':
            _executor = concurrent.futures.ThreadPoolExecutor
        elif executor_type == 'process':
            _executor = concurrent.futures.ProcessPoolExecutor
        else:
            raise ValueError("{} is not a valid executor type.".format(executor_type))
        return _executor(max_workers=executor_max_workers)

    def _prepare_fn(self, fn, force_copy=False):
        if isinstance(self._self, concurrent.futures.ThreadPoolExecutor) \
            or force_copy:
            fn = copy_current_request_context(fn)
            if current_app.config[self.EXECUTOR_PUSH_APP_CONTEXT]:
                fn = push_app_context(fn)
        return fn

    def submit(self, fn, *args, **kwargs):
        r"""Schedules the callable, fn, to be executed as fn(\*args \**kwargs)
        and returns a :class:`~flask_executor.futures.FutureProxy` object, a
        :class:`~concurrent.futures.Future` subclass representing
        the execution of the callable.

        See also :meth:`concurrent.futures.Executor.submit`.

        Callables are wrapped a copy of the current application context and the
        current request context. Code that depends on information or
        configuration stored in :data:`flask.current_app`,
        :data:`flask.request` or :data:`flask.g` can be run without
        modification.

        Note: Because callables only have access to *copies* of the application
        or request contexts any changes made to these copies will not be
        reflected in the original view. Further, changes in the original app or
        request context that occur after the callable is submitted will not be
        available to the callable.

        Example::

            future = executor.submit(pow, 323, 1235)
            print(future.result())

        :param fn: The callable to be executed.
        :param \*args: A list of positional parameters used with
                       the callable.
        :param \**kwargs: A dict of named parameters used with
                          the callable.

        :rtype: flask_executor.FutureProxy
        """
        fn = self._prepare_fn(fn)
        future = self._self.submit(fn, *args, **kwargs)
        for callback in self._default_done_callbacks:
            future.add_done_callback(callback)
        return FutureProxy(future, self)

    def submit_stored(self, future_key, fn, *args, **kwargs):
        r"""Submits the callable using :meth:`Executor.submit` and stores the
        Future in the executor via a
        :class:`~flask_executor.futures.FutureCollection` object available at
        :data:`Executor.futures`. These futures can be retrieved anywhere
        inside your application and queried for status or popped from the
        collection. Due to memory concerns, the maximum length of the
        FutureCollection is limited, and the oldest Futures will be dropped
        when the limit is exceeded.

        See :class:`flask_executor.futures.FutureCollection` for more
        information on how to query futures in a collection.

        Example::

            @app.route('/start-task')
            def start_task():
                executor.submit_stored('calc_power', pow, 323, 1235)
                return jsonify({'result':'success'})

            @app.route('/get-result')
            def get_result():
                if not executor.futures.done('calc_power'):
                    future_status = executor.futures._state('calc_power')
                    return jsonify({'status': future_status})
                future = executor.futures.pop('calc_power')
                return jsonify({'status': done, 'result': future.result()})

        :param future_key: Stores the Future for the submitted task inside the
                           executor's ``futures`` object with the specified
                           key.
        :param fn: The callable to be executed.
        :param \*args: A list of positional parameters used with
                       the callable.
        :param \**kwargs: A dict of named parameters used with
                          the callable.

        :rtype: concurrent.futures.Future
        """
        future = self.submit(fn, *args, **kwargs)
        self.futures.add(future_key, future)
        return future

    def map(self, fn, *iterables, **kwargs):
        r"""Submits the callable, fn, and an iterable of arguments to the
        executor and returns the results inside a generator.

        See also :meth:`concurrent.futures.Executor.map`.

        Callables are wrapped a copy of the current application context and the
        current request context. Code that depends on information or
        configuration stored in :data:`flask.current_app`,
        :data:`flask.request` or :data:`flask.g` can be run without
        modification.

        Note: Because callables only have access to *copies* of the application
        or request contexts
        any changes made to these copies will not be reflected in the original
        view. Further, changes in the original app or request context that
        occur after the callable is submitted will not be available to the
        callable.

        :param fn: The callable to be executed.
        :param \*iterables: An iterable of arguments the callable will apply to.
        :param \**kwargs: A dict of named parameters to pass to the underlying
                          executor's :meth:`~concurrent.futures.Executor.map`
                          method.
        """
        fn = self._prepare_fn(fn)
        return self._self.map(fn, *iterables, **kwargs)

    def job(self, fn):
        """Decorator. Use this to transform functions into `ExecutorJob`
        instances that can submit themselves directly to the executor.

        Example::

            @executor.job
            def fib(n):
                if n <= 2:
                    return 1
                else:
                    return fib(n-1) + fib(n-2)

            future = fib.submit(5)
            results = fib.map(range(1, 6))
        """
        if isinstance(self._self, concurrent.futures.ProcessPoolExecutor):
            raise TypeError(
                "Can't decorate {}: Executors that use multiprocessing "
                "don't support decorators".format(fn)
            )
        return ExecutorJob(executor=self, fn=fn)

    def add_default_done_callback(self, fn):
        """Registers callable to be attached to all newly created futures. When a
        callable is submitted to the executor,
        :meth:`concurrent.futures.Future.add_done_callback` is called for every default
        callable that has been set."

        :param fn: The callable to be added to the list of default done callbacks for new
                   Futures.
        """

        self._default_done_callbacks.append(fn)
