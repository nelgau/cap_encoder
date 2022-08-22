import os
import sys
import logging
import tempfile
from functools import wraps



def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if len(logger.handlers) == 0:
        handler1 = logging.StreamHandler(sys.stderr)

        log_path = os.path.dirname(__file__)
        log_file = os.path.join(log_path, "cap_encoder_gen.log")

        handler2 = None
        try:
            handler2 = logging.FileHandler(log_file)
        except PermissionError:
            log_path = os.path.join(tempfile.mkdtemp()) 
            try: # Use try/except here because python 2.7 doesn't support exist_ok
                os.makedirs(log_path)
            except:
                pass
            log_file = os.path.join(log_path, "cap_encoder_gen.log")
            handler2 = logging.FileHandler(log_file)
        
        handler1.setLevel(logging.DEBUG)
        handler2.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s %(name)s %(lineno)d:%(message)s", datefmt="%m-%d %H:%M:%S"
        )
        handler1.setFormatter(formatter)
        handler2.setFormatter(formatter)

        logger.addHandler(handler1)
        logger.addHandler(handler2)

    return logger

def log_exception(reraise=False):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                get_logger().exception(e, exc_info=True)
                if reraise:
                    raise e
        return wrapper
    return decorator
