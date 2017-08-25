from __future__ import print_function
from .settings import settings
import requests


def verify_key(key):
    r = requests.post('http://%s/api/admin/verifyHash' %
                      settings.CATALEARN_URL, data={'hash': key})
    if r.status_code == 200:
        return True
    else:
        return False
