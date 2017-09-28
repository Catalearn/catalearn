
class Settings():
    def __init__(self):
        self.LOCAL = False
        self.CATALEARN_URL = 'catalearn.com'
        self.API_KEY = None
        self.GPU_PORT = 8000
        self.CURRENT_JOB_HASH = None
        self.SERVER = False

    # record the file downloads in a file so that we can get rid of them when we download the results
    def record_file_download(self, file_name):
        if self.SERVER:
            with open('.download_records', 'a') as f:
                f.write(file_name + '\n')

settings = Settings()
