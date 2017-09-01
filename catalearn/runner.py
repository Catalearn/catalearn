from __future__ import print_function
import ast
import re
import inspect
import dill
from .connector import (contact_server, upload_data, stream_output, 
    get_result, get_time_and_credit, get_info_from_hash,  stop_job_with_hash)

def format(sourceLines):  # removes indentation
    head = sourceLines[0]
    while head[0] == ' ' or head[0] == '\t':
        sourceLines = [l[1:] for l in sourceLines]
        head = sourceLines[0]
    return sourceLines

def reconnect_to_job(jobHash):
    (status, ip, wsPort) = get_info_from_hash(jobHash)
    if status == 'running':
        print('Job reconnected:')
        success = stream_output(ip, wsPort, jobHash, False)
        if not success:
            return None
    else:
        print('Job has finished')
    result = get_result(ip, jobHash)
    get_time_and_credit(jobHash)
    return result

def stop_job(jobHash):
    (status, ip, wsPort) = get_info_from_hash(jobHash)
    if status == 'running':
        stop_job_with_hash(jobHash)
        print('Job is Now stopped')
    else:
        print('Job is already stopped')


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

        # if the user cancelled the upload, just return None
        success = upload_data(gpuIp, jobHash)
        if not success: 
            return None
        # prints all the output of the code being run
        success = stream_output(gpuIp, wsPort, jobHash, interrupt)
        if not success:
            return None
        result = get_result(gpuIp, jobHash)
        get_time_and_credit(jobHash)
        return result

    return gpu_func
