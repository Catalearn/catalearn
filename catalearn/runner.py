from __future__ import print_function
import inspect
import dill
import sys

from .custom_exceptions import *
from .connector import *


def format(sourceLines):  # removes indentation
    head = sourceLines[0]
    while head[0] == ' ' or head[0] == '\t':
        sourceLines = [l[1:] for l in sourceLines]
        head = sourceLines[0]
    return sourceLines

def get_source_code(func):
    source_lines = inspect.getsourcelines(func)[0]
    source_lines = format(source_lines)
    if source_lines[0][0] == '@':
        # if the first line is a decorator, remove it
        source_lines = source_lines[1:]  
    source = ''.join(source_lines)
    return source

def print_new_files(new_files):
    if new_files:
        print('New file%s downloaded: %s' % ('' if len(new_files) == 1 else 's', str(new_files)[1:-1]))

def print_time_credit(job_hash):
    duration, credit = get_time_and_credit(job_hash)
    if duration == 0:
        print('Your job took less than a minute, so its free!')
    else:
        print('%s minute%s used, you have %s minute%s of credit remaining' % (
            duration, '' if duration <= 1 else 's',
            credit, '' if credit <= 1 else 's'))

def abort_and_print_credit():
    if settings.CURRENT_JOB_HASH:
        abort_job(settings.CURRENT_JOB_HASH)
        print('Job aborted')
        print_time_credit(settings.CURRENT_JOB_HASH)
    sys.tracebacklimit = 0
    sys.exit()
# decorator that handles the possible errors
def add_error_handling(run_job_func):

    def wrap(*args, **kwargs):
        try:
            return run_job_func(*args, **kwargs)

        # all keyboard interrupt during streaming will be caught and raised as JobInterruptedException
        # anything here will be during upload or download, so we just abort
        except KeyboardInterrupt as e:
            print('Job aborted')
            abort_and_print_credit()

        except RequestFailedException as e:
            print('Oops, something went wrong...')
            print(e.error_msg)
            print('Please try again later')
            sys.tracebacklimit = 0
            sys.exit()

        except JobInterruptedException as e:
            # extra newline incase no newline was printed
            print('\nJob interrupted')
            ans = input('Do you want to abort the job?\n')
            if ans == 'yes':
                abort_and_print_credit()
            else:
                print('Job is still running\n')
                print('To reconnect to the job:\n')
                print('    catalearn.reconnect()\n')
                print('To stop the job:\n')
                print('    catalearn.stop()\n')

    return wrap


@add_error_handling
def reconnect_to_job():
    # ask for a list of unfinished jobs
    # this includes jobs that have finished but haven't returned the result
    unreturned_jobs = get_unreturned_jobs()
    if not unreturned_jobs:
        print('No running jobs')
        return

    # we are only looking at one job right now, may extend this in the future
    job_hash, status, gpu_ip, ws_port = unreturned_jobs[0]
    # we set the global job_hash so that we know which job to abort if things go wrong
    settings.CURRENT_JOB_HASH = job_hash
    if status == 'running':
        print('Job reconnected:')
        # reconnect the websocket
        stream_output(gpu_ip, ws_port, job_hash)
        print('Job finished') 
        print('Downloading result')
        result, new_files = get_result(gpu_ip, job_hash)

    elif status == 'uploaded':
        # the GPU server has been shut down
        # make a call to catalearn to retrieve the result
        print('Job finished') 
        print('Downloading result')
        result, new_files = get_uploaded_result(job_hash)

    elif status == 'finished':
        # results still on the GPU
        print('Job finished') 
        print('Downloading result')
        result, new_files = get_result(gpu_ip, job_hash)
    
    else:
        raise ValueError('invalid status: ' + status)

    print_new_files(new_files)
    print_time_credit(job_hash)
    return result


@add_error_handling
def stop_job():
    running_jobs = get_running_jobs()
    if running_jobs:
        # only dealing with one job for now
        job_hash, _, _, _ = running_jobs[0]
        abort_job(job_hash)
        print('Job is Now stopped')
    else:
        print('No jobs running right now')


def decorate_gpu_func(func):

    @add_error_handling
    def gpu_func(*args, **kwargs):
        data = {}
        data['source'] = get_source_code(func)
        data['args'] = args
        data['kwargs'] = kwargs
        data['name'] = func.__name__
        data_path = "uploads.pkl"
        dill.dump(data, open(data_path, "wb"))

        job_hash, has_idle_instance, instance_id = get_available_instance()
        # we set the global job_hash so that we know which job to abort if things go wrong
        settings.CURRENT_JOB_HASH = job_hash
        # no idle GPU available, catalearn is starting one, 
        # we need to ping it to see if it has started
        if not has_idle_instance:
            print("Starting server, this will take about 20 seconds")
            ping_until_gpu_start(instance_id)
            print("Server started")

        gpu_ip, ws_port = get_ip_and_ws_port(job_hash)
        print("Uploading data")
        upload_data(gpu_ip, job_hash, data_path)
        print("Job running:")
        stream_output(gpu_ip, ws_port, job_hash)
        print('Job finished') 
        print('Downloading result')
        result, new_files = get_result(gpu_ip, job_hash)
        print("Done!")
        print_new_files(new_files)
        print_time_credit(job_hash)
        return result
            

    return gpu_func


