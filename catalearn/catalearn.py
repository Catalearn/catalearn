from __future__ import print_function
import sys
import dill
import inspect

from .runner import decorate_gpu_func
from .saver import *
from .admin import verify_key
from .settings import settings

def set_debug():
    settings.LOCAL = True
    settings.CATALEARN_URL = 'localhost:8080'

def login(key):
    verified = verify_key(key)
    if verified:
        settings.API_KEY = key
        print('Login successful')
    else:
        print('Login failed, unverified key')

def run_on_gpu(interrupt=True):
    def wrap(func):
        if settings.API_KEY is None:
            print('Not Loged in, running code locally instead')
            return None
        return decorate_gpu_func(func, interrupt)
    return wrap

def get_last_result():
    pass

def save_data(data):
    pass
