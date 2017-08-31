from __future__ import print_function
import sys
import dill
import inspect

from .runner import decorate_gpu_func, reconnect_to_job, stop_job
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

def login_check():
    if settings.API_KEY is None:
        print('Not Logged in, please use catalearn.login() to log in first')
        sys.exit()

def run_on_gpu(func):
    login_check()
    return decorate_gpu_func(func, True)

def run_uninterrupted(func):
    login_check()
    return decorate_gpu_func(func, False)

def reconnect(jobHash):
    login_check()
    return reconnect_to_job(jobHash)

def stop(jobHash):
    login_check()
    stop_job(jobHash)

def save_data(data):
    pass
