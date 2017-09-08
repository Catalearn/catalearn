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
    print('Uploading \'%s\'' data_name)

    url = 'http://%s/api/save_on_aws/save_on_aws' % settings.CATALEARN_URL

    data = {
        'user_hash': user_hash,
        'file_name': data_name,
        'file': ( 'data', data_buffer, 'application/octet-stream'),
    }
    encoder = MultipartEncoder(
        fields=data
    )
    total = data_buffer.getbuffer().nbytes
    sys.stdout.flush()
    pbar = tqdm(total=total, unit='B', unit_scale=True)
    def callback(monitor):
        progress = monitor.bytes_read - callback.last_bytes_read
        pbar.update(progress)
        callback.last_bytes_read = monitor.bytes_read
    callback.last_bytes_read = 0

    monitor = MultipartEncoderMonitor(encoder, callback) 

    server_resp = requests.post(url, data=monitor, headers={'Content-Type': monitor.content_type})
    pbar.close()

    if (server_resp.status_code != 200):
        print("Error saving \'%s\' to the cloud" % data_name)
    else:
        print("Successfully uploaded \'%s\' to the cloud" % data_name)
    return
    

def download_from_cloud(data_name):
    if (not isinstance(data_name, str)):
        print("data_name must be a string")
        return

    user_hash = settings.API_KEY

    # Now send the post request to the catalearn server
    server_resp = requests.post('http://%s/api/save_on_aws/download' % settings.CATALEARN_URL,
                                data={
                                    "user_hash": user_hash,
                                    "file_name": data_name
                                }, stream=True)

    if server_resp.status_code != 200:
        if server_resp.status_code == 404:
            return print('\'%s\' is not found' % data_name)
        else:
            return print('Invalid request')

    total_size = int(server_resp.headers.get('content-length', 0))
    raw = io.BytesIO()

    print('Downloading %s' % data_name)
    for data in tqdm(server_resp.iter_content(32 * 1024), total=total_size, unit='B', unit_scale=True):
        raw.write(data)

    print("Successfully downloaded \'%s\' from the cloud" % data_name)

    result = dill.loads(raw.getvalue())
    return result
