"""VALIDATORS"""

from functools import wraps

from gladAnalysis.routes.api import error
import logging

def validate_greeting(func):
    """Validation"""
    @wraps(func)

    def wrapper(*args, **kwargs):
        logging.info('in validator')
        if False:
            return error(status=400, detail='Validating something in the middleware')
        return func(*args, **kwargs)
    return wrapper
