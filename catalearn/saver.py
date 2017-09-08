from .settings import settings
import requests
from tqdm import tqdm
import io
import dill
from os import path
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import sys


def save_var_to_cloud(data_var, data_name):

    if (not isinstance(data_name, str)):
        print("data_name must be a string")
        return

    user_hash = settings.API_KEY
    data_buffer = io.BytesIO(dill.dumps(data_var))
    print('Uploading \'%s\'...' % data_name)

    url = 'http://%s/api/save/getUploadUrl' % settings.CATALEARN_URL
    r = requests.post(url, data={
        'user_hash': user_hash,
        'file_name': data_name
    })
    if r.status_code != 200:
        raise RuntimeError(r.text)

    presigned_url = r.content

    r = requests.put(presigned_url, data=data_buffer)

    if (r.status_code != 200):
        print("Error saving \'%s\' to the cloud: %s" % (data_name, r.content))
    else:
        print("Successfully uploaded \'%s\' to the cloud" % data_name)
    return


def download_from_cloud(data_name):
    if (not isinstance(data_name, str)):
        print("data_name must be a string")
        return

    user_hash = settings.API_KEY

    url = 'http://%s/api/save/getDownloadUrl' % settings.CATALEARN_URL
    r = requests.post(url, data={
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
    for data in tqdm(r.iter_content(32 * 1024), total=total_size, unit='B', unit_scale=True):
        raw.write(data)

    print("Successfully downloaded \'%s\' from the cloud" % data_name)

    result = dill.loads(raw.getvalue())
    return result
