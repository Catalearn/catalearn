from .settings import settings
from hashlib import sha1
import requests
import json

#Imports that are just used for testing
import sys

def save_var_to_cloud(data):
    #Will first get the json encoding of the data and send that off to be saved to allow saving
    #of arrays and stuff. Is this how it should be done?

    # Remove and settings.LOCAL = False thats just there for debugging
    if (settings.API_KEY == None and settings.LOCAL == False):
        print("Not logged in, unable to save data")
        return

    #First get a name unique to this data
    #Will need to change otherwise user will have new copies of their variable everytime they 
    #change a value
    hashing_obj = sha1()
    if (isinstance(data, str)):
        hashing_obj.update(bytes(data, 'utf-8'))
    else:
        hashing_obj.update(bytes(data))
    data_name = hashing_obj.digest()

    #Assuming the users hash is equal to their API_KEY. Is it?
    user_hash = settings.API_KEY

    #For debugging purposes
    if (user_hash == None):
        user_hash = 'test_user_hash_from_python'


    #Now send the post request to the catalearn server
    server_resp = requests.post('http://%s/api/save_on_aws/save_on_aws' % settings.CATALEARN_URL,
        data = {
            "user_hash": user_hash,
            "file_name": data_name,
            "data": json.dumps(data),
        }
    )
    if (server_resp.status_code != 200):
        print("Error saving variable to cloud")
    return
