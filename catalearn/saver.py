from .settings import settings
import requests

def save_var_to_cloud(data, data_name):

    if (settings.API_KEY == None):
        print("Not logged in, unable to save data")
        return

    if (not isinstance(data_name, str)):
        print("data_name must be a string")
        return

    user_hash = settings.API_KEY

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
