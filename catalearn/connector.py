from __future__ import print_function
import time
import json
import dill
from tqdm import tqdm
import sys
import io
from zipfile import ZipFile
from os import path, remove, listdir, rename
from shutil import rmtree
import requests
from websocket import create_connection
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from .settings import settings
from .custom_exceptions import *


def status_check(res):
    if res.status_code != 200:
        raise RequestFailedException(res.text)

def get_available_instance():
    if settings.LOCAL:
        server_type = 'local'
    else:
        server_type = 'gpu'
    r = requests.post('http://%s/api/gpu/getAvailableInstance' % settings.CATALEARN_URL,
                      data={'username': settings.API_KEY,
                            'type': server_type})
    status_check(r)
    res = r.json()
    job_hash = res['jobHash']
    idle = res['idle']
    instance_id = res['instanceId']
    return (job_hash, idle, instance_id)

def ping_until_gpu_start(instance_id):
    while True:
        r = requests.post('http://%s/api/gpu/checkStatus' % settings.CATALEARN_URL,
                            data={'instanceId': instance_id})
        status_check(r)
        res = r.json()
        if res['started']:
            break
        time.sleep(3)
        print('.', end='')
        sys.stdout.flush()
    print()

def get_ip_and_ws_port(job_hash):
    r = requests.post('http://%s/api/gpu/getIpPort' % settings.CATALEARN_URL,
                      data={'hash': job_hash})
    status_check(r)
    res = r.json()
    return (res['ip'], res['ws_port'])


def upload_data(gpu_ip, job_hash, data_path):
    url = 'http://%s:%s/runJobDecorator' % (gpu_ip, settings.GPU_PORT)
    file_size = path.getsize(data_path)
    pbar = tqdm(total=file_size, unit='B', unit_scale=True)

    def callback(monitor):
        progress = monitor.bytes_read - callback.last_bytes_read
        pbar.update(progress)
        callback.last_bytes_read = monitor.bytes_read
    callback.last_bytes_read = 0

    with open(data_path, 'rb') as f:
        data = {
            'file': ('uploads.pkl', f, 'application/octet-stream'),
            'hash': job_hash
        }
        encoder = MultipartEncoder(
            fields=data
        )
        monitor = MultipartEncoderMonitor(encoder, callback)
        r = requests.post(url, data=monitor, headers={
            'Content-Type': monitor.content_type})

    remove(data_path)
    # pbar might not close when the user interrupts, need to fix this
    pbar.close()
    status_check(r)



def stream_output(gpu_ip, ws_port, job_hash):
    # connect to the websocket for this job
    url = 'ws://%s:%s' % (gpu_ip, ws_port)
    ws = create_connection(url)
    # send over the job hash to start the job
    ws.send(job_hash)
    # print all the outputs of the script to the screen
    try:
        while True:
            msg = ws.recv()
            msgJson = json.loads(msg)
            if 'end' in msgJson:
                break
            else:
                print(msgJson['message'], end='')
        ws.close()

    # if the user interrupts the job, decide whether or not to stop
    except KeyboardInterrupt:
        # propagate the exception for the layer above to handle
        raise JobInterruptedException()


def download_and_unzip_result(url, job_hash):
    r = requests.post(url, data={'hash': job_hash}, stream=True)
    status_check(r)
    total_size = int(r.headers.get('content-length', 0))
    with open('download.zip', 'wb') as f:
        pbar = tqdm(total=total_size, unit='B', unit_scale=True)
        chunck_size = 1024 * 32  # 32kb
        for data in r.iter_content(chunk_size=chunck_size):
            f.write(data)
            pbar.update(chunck_size)
        # again there might be a pbar issue here
        pbar.close()

    zip_content = open("download.zip", "rb").read()
    z = ZipFile(io.BytesIO(zip_content))
    z.extractall()
    remove('download.zip')

    result = None # output of the script
    new_files = None # names of new files created by the script

    pickle_path = path.abspath(path.join(job_hash, job_hash + '.pkl'))
    if path.isfile(pickle_path):
        with open(pickle_path, 'rb') as f:
            # Hack: a workaround for dill's pickling problem
            # import_all()  
            result = dill.load(f)
            # unimport_all()
        remove(pickle_path)

    if path.isdir(job_hash):
        new_files = listdir(job_hash)
        for name in new_files:
            rename(path.join(job_hash, name), name)
        rmtree(job_hash)

    return result, new_files


def get_uploaded_result(job_hash):
    url = 'http://%s/api/gpu/getUploadedResult' % settings.CATALEARN_URL
    return download_and_unzip_result(url, job_hash)


def get_result(gpu_ip, job_hash):
    url = 'http://%s:%s/getResult' % (gpu_ip, settings.GPU_PORT)
    return download_and_unzip_result(url, job_hash)


def get_time_and_credit(jobHash):
    r = requests.post('http://%s/api/gpu/getTimeAndCredit' % settings.CATALEARN_URL,
                      data={'hash': jobHash})
    status_check(r)
    res = r.json()
    return (res['time'], res['credits'])

# abort a job, could happen at any stage
def abort_job(job_hash):
    url = 'http://%s/api/gpu/abortJob' % settings.CATALEARN_URL
    r = requests.post(url, data={'hash': job_hash})
    status_check(r)

# returns info about all jobs that are either 'running' or 'results_uploaded'
def get_unreturned_jobs():
    r = requests.post('http://%s/api/gpu/getUnreturnedJobs' % settings.CATALEARN_URL,
                      data={'key': settings.API_KEY})
    status_check(r)
    res = r.json()
    # convert the dictionary to tuples
    unreturned_jobs = [(
        x['hash'],
        x['status'],
        x['ip'],
        x['wsPort']
    ) for x in res]

    return unreturned_jobs

# returns info about all 'running' jobs
def get_running_jobs():
    unreturned_jobs = get_unreturned_jobs()
    # x[1] corresponds to the status
    return [x for x in unreturned_jobs if x[1] == 'running']



