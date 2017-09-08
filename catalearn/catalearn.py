from __future__ import print_function
import sys
import dill
import inspect

from .runner import decorate_gpu_func, reconnect_to_job, stop_job
from .saver import save_var_to_cloud, download_from_cloud
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
    return decorate_gpu_func(func)

def reconnect():
    login_check()
    return reconnect_to_job()

def stop():
    login_check()
    stop_job()

def save(data, name):
    login_check()
    save_var_to_cloud(data, name)

def load(name):
    login_check()
    return download_from_cloud(name)
