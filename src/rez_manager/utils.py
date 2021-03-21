import logging


def catch_exception(fn):
    """A decorator that catches exceptions and logs them.

    Args:
        fn (function): The function to catch exceptions.
    """
    def _wrapper(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except Exception:
            logger = logging.getLogger('rez_manager')
            logger.exception('Exception encountered.')

    return _wrapper
