from __future__ import print_function
import requests
from websocket import create_connection
import time
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import json
import dill
from tqdm import tqdm
import sys
from zipfile import ZipFile
from os import path, remove
from .settings import settings


def statusCheck(res):
    if res.status_code != 200:
        print(res.text)
        sys.exit()

def contact_server():
    if settings.LOCAL:
        serverType = 'local'
    else:
        serverType = 'gpu'
    r = requests.post('http://%s/api/gpu/checkAvailability' % settings.CATALEARN_URL,
                      data={'username': settings.API_KEY,
                            'type': serverType})
    statusCheck(r)
    res = r.json()

    jobHash = res['jobHash']
    idle = res['idle']
    instanceId = res['instanceId']

    if not idle:
        print("Starting server, this will take about 20 seconds")
        while True:
            r = requests.post('http://%s/api/gpu/checkStatus' % settings.CATALEARN_URL,
                              data={'instanceId': instanceId})
            statusCheck(r)
            res = r.json()
            if res['started']:
                break
            time.sleep(3)
            print('.', end='')
        print()

    r = requests.post('http://%s/api/gpu/runJob' % settings.CATALEARN_URL,
                      data={'hash': jobHash})
    statusCheck(r)
    res = r.json()
    gpuIp = res['ip']
    wsPort = res['ws_port']
    return (gpuIp, wsPort, jobHash)


def upload_data(gpuIp, jobHash):
    url = 'http://%s:%s/runJobDecorator' % (gpuIp, settings.GPU_PORT)
    print("Uploading data")

    fileSize = path.getsize('uploads.pkl')
    pbar = tqdm(total=fileSize, unit='B', unit_scale=True)

    def callback(monitor):
        progress = monitor.bytes_read - callback.last_bytes_read
        pbar.update(progress)
        callback.last_bytes_read = monitor.bytes_read
    callback.last_bytes_read = 0

    with open('uploads.pkl', 'rb') as file:
        data = {
            'file': ('uploads.pkl', file, 'application/octet-stream'),
            'hash': jobHash
        }
        encoder = MultipartEncoder(
            fields=data
        )
        monitor = MultipartEncoderMonitor(encoder, callback)
        try:
            r = requests.post(url, data=monitor, headers={
                'Content-Type': monitor.content_type})
            pbar.close()
            statusCheck(r)
            remove('uploads.pkl')
            return True
        except:
            pbar.close() # need to close before printing anything
            print('Upload cancelled')
            remove('uploads.pkl')
            return False
    
def stream_output(gpuIp, wsPort, jobHash):

    gpuUrl = 'ws://%s:%s' % (gpuIp, wsPort)
    ws = create_connection(gpuUrl)
    outUrl = None
    ws.send(jobHash)
    try:
        while True:
            msg = ws.recv()
            msgJson = json.loads(msg)
            if 'end' not in msgJson:
                print(msgJson['message'], end='')
            else:
                if 'downloadUrl' in msgJson:
                    outUrl = msgJson['downloadUrl']
                else:
                    outUrl = None
                break
    except KeyboardInterrupt:
        print('\nJob interrupted')
    finally:
        ws.close()
        return outUrl


def get_result(outUrl, jobHash):

    print("Downloading result")
    r = requests.post(outUrl, data={'hash': jobHash}, stream=True)
    if r.status_code != 200:
        return None

    totalSize = int(r.headers.get('content-length', 0))
    with open('download.zip', 'wb') as f:
        pbar = tqdm(total=totalSize, unit='B', unit_scale=True)
        chunckSize = 32768
        for data in r.iter_content(chunckSize):
            f.write(data)
            pbar.update(chunckSize)
        pbar.close()

    with ZipFile('download.zip', 'r') as zipData:
        fileNames = zipData.namelist()

        for name in fileNames:
            data = zipData.read(name)
            with open(name, 'wb') as file:
                file.write(data)

    result = None

    if path.isfile(jobHash):
        with open(jobHash, "rb") as f:

            # import_all()  # Hack: a workaround for dill's pickling problem
            result = dill.load(f)
            # unimport_all()
            if result is None:
                print('Computation failed')
            print("Done!")

    remove(jobHash)
    remove('download.zip')
    fileNames.remove(jobHash)
    if fileNames:
        print('New files: %s' % str(fileNames)[1:-1])

    return result

    
