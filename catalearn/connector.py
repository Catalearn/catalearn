from __future__ import print_function
import requests
from websocket import create_connection
import time
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import json
import dill
from tqdm import tqdm
import sys
import io
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

def fixBadZipfile(zipFile):  
     f = open(zipFile, 'r+b')  
     data = f.read()  
     pos = data.find('\x50\x4b\x05\x06') # End of central directory signature  
     if (pos > 0):  
         print("Truncating file at location " + str(pos + 22) + ".")  
         f.seek(pos + 22)   # size of 'ZIP end of central directory record' 
         f.truncate()  
         f.close()  
     else:  
         pass
         # raise error, file is truncated 

def get_result(outUrl, jobHash):

    print("Downloading result")
    print(outUrl)
    r = requests.post(outUrl, data={'hash': jobHash})
    statusCheck(r)

    totalSize = int(r.headers.get('content-length', 0))
    with open('download.zip', 'wb') as f:
        pbar = tqdm(total=totalSize, unit='B', unit_scale=True)
        chunckSize = 32768
        for data in r.iter_content(chunk_size=chunckSize):
            f.write(data)
            pbar.update(chunckSize)
        pbar.close()

    z = ZipFile(io.BytesIO(r.content))
    z.extractall()
    newFiles = z.namelist()

    result = None
    if path.isfile(jobHash):
        with open(jobHash, "rb") as f:

            # import_all()  # Hack: a workaround for dill's pickling problem
            result = dill.load(f)
            # unimport_all()
            print("Done!")
            remove(jobHash)
            newFiles.remove(jobHash)

    remove('download.zip')

    printedNameList = str(newFiles)[1:-1]
    if len(newFiles) == 1:
        print('New file: %s' % printedNameList)
    elif len(newFiles) > 1:
        print('New files: %s' % printedNameList)

    return result

    
