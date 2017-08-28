from .settings import settings
from hashlib import sha1
import requests
import json
import datetime

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
    #Temp just get time now
    data_name = str(datetime.datetime.now()).replace(" ", "_")

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
            "data": data,
        }
    )
    if (server_resp.status_code != 200):
        print("Error saving variable to cloud")
    else:
        print("Successfully uploaded data to the cloud")
    return
