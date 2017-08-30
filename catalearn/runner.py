from __future__ import print_function
import ast
import re
import inspect
import dill
from .connector import (contact_server, upload_data, stream_output, 
    get_result, get_time_and_credit)


currentHash = None

def format(sourceLines):  # removes indentation
    head = sourceLines[0]
    while head[0] == ' ' or head[0] == '\t':
        sourceLines = [l[1:] for l in sourceLines]
        head = sourceLines[0]
    return sourceLines


def retrieveResultFromLastJob():
    if currentHash is None:
        return None

    result = get_result(outUrl, jobHash)
    get_time_and_credit(jobHash)
    return result


def decorate_gpu_func(func, interrupt):

    def gpu_func(*args, **kwargs):

        sourceLines = inspect.getsourcelines(func)[0]
        sourceLines = format(sourceLines)
        sourceLines = sourceLines[1:]  # remove the decorator
        source = ''.join(sourceLines)
        data = {}
        data['source'] = source
        data['args'] = args
        data['kwargs'] = kwargs
        data['name'] = func.__name__

        dill.dump(data, open("uploads.pkl", "wb"))

        gpuIp, wsPort, jobHash = contact_server(interrupt)
        # if not in interrupt mode, we store the hash 
        # so that the user can still retrieve the results later
        if not interrupt:
            currentHash = jobHash
        success = upload_data(gpuIp, jobHash)
        if not success:
            return None
        outUrl = stream_output(gpuIp, wsPort, jobHash)
        if not outUrl:
            return None
        result = get_result(outUrl, jobHash)
        get_time_and_credit(jobHash)
        return result

    return gpu_func
