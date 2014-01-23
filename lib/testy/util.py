"""
Utility functions for testing
"""
import types

_MAX_LENGTH = 80


class MockException(Exception):
    pass


def safe_repr(obj, short=False):
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if not short or len(result) < _MAX_LENGTH:
        return result
    return result[:_MAX_LENGTH] + ' [truncated]...'


def set_exception_response(mock_obj, exception=None):
    """
    Sets the given exception as the response to the function invocation of the
    given mock object.

    :param mock_obj:
    :param exception: defaults to generic MockException
    """
    if exception is None:
        exception = MockException()

    def err(*args, **kwargs):
        raise exception
    mock_obj.side_effect = err


def bind_instance_method(instance, method_name, method):
    """
    Convenience function that binds the given method to the instance.

    :param instance class instance
    :param method_name method name to bind
    :param method method implementation; should have expected args of method
    """
    method = types.MethodType(method, instance, instance.__class__)
    setattr(instance, method_name, method)
