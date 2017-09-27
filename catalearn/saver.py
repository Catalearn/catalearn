from .settings import settings
import requests
from tqdm import tqdm
import io
import dill
from os import path
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import sys


def save_var_cloud(data_var, data_name):
    if not isinstance(data_name, str):
        print("data_name must be a string")
        return

    user_hash = settings.API_KEY
    data_buffer = io.BytesIO(dill.dumps(data_var))
    print('Uploading %s...' % data_name)

    url = 'http://%s/api/save/getUploadUrl' % settings.CATALEARN_URL
    r = requests.post(url, data={
        'type': 'variable',
        'user_hash': user_hash,
        'file_name': data_name
    })
    if r.status_code != 200:
        raise RuntimeError(r.text)

    presigned_url = r.content

    r = requests.put(presigned_url, data=data_buffer)

    if (r.status_code != 200):
        print("Error saving %s\: %s" % (data_name, r.content))
    else:
        print("Successfully uploaded %s" % data_name)
    return

def save_file_cloud(file_path):

    if not path.exists(file_path):
        print('%s does not exist' % file_path)
        return

    user_hash = settings.API_KEY
    save_name = path.basename(file_path)
    print('Uploading %s...' % save_name)
    url = 'http://%s/api/save/getUploadUrl' % settings.CATALEARN_URL
    r = requests.post(url, data={
        'type': 'file',
        'user_hash': user_hash,
        'file_name': save_name
    })
    if r.status_code != 200:
        raise RuntimeError(r.text)

    presigned_url = r.content
    with open(file_path, 'rb') as f:
        r = requests.put(presigned_url, data=f)

    if (r.status_code != 200):
        print("Error uploading %s\: %s" % (save_name, r.content))
    else:
        print("Successfully uploaded %s" % save_name)
    return


def download_var_cloud(data_name):
    if not isinstance(data_name, str):
        print("data_name must be a string")
        return

    user_hash = settings.API_KEY

    url = 'http://%s/api/save/getDownloadUrl' % settings.CATALEARN_URL
    r = requests.post(url, data={
        'type': 'variable',
        'user_hash': user_hash,
        'file_name': data_name
    })
    if r.status_code != 200:
        raise RuntimeError(r.text)

    presigned_url = r.content

    # Now send the post request to the catalearn server
    r = requests.get(presigned_url, stream=True)

    total_size = int(r.headers.get('content-length', 0))
    raw = io.BytesIO()

    print('Downloading %s' % data_name)
    for data in r.iter_content(32 * 1024):
        raw.write(data)

    print("Successfully downloaded %s " % data_name)

    result = dill.loads(raw.getvalue())
    return result

def download_file_url(url):
    if not isinstance(url, str):
        print("url must be a string")
        return

    file_name = path.basename(url)
    res = requests.get(url, stream=True)
    print('Downloading %s' % file_name)

    with open(file_name, 'wb')as file_handle:
        for data in res.iter_content(32 * 1024):
            file_handle.write(data)
    print("Download successful") 


def download_file_cloud(file_name):
    if not isinstance(file_name, str):
        print("file_name must be a string")
        return

    user_hash = settings.API_KEY

    url = 'http://%s/api/save/getDownloadUrl' % settings.CATALEARN_URL
    r = requests.post(url, data={
        'type': 'file',
        'user_hash': user_hash,
        'file_name': file_name
    })
    if r.status_code != 200:
        raise RuntimeError(r.text)

    presigned_url = r.content

    # Now send the post request to the catalearn server
    res = requests.get(presigned_url, stream=True)
    print('Downloading %s' % file_name)

    with open(file_name, 'wb')as file_handle:
        for data in res.iter_content(32 * 1024):
            file_handle.write(data)
    print("Download successful")
