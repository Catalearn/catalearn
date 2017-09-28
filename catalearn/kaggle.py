import sys
import os
import pickle
import re
from .settings import settings

from mechanicalsoup import Browser

if settings.ISIPYTHON:
    from tqdm import tqdm_notebook as tqdm
else:
    from tqdm import tqdm

class Kaggle():
    def __init__(self):
        self.login_browser = None

    def login(self, username, password):
        if not self.login_browser:
            self.login_browser = self.get_login_browser(username, password)
            print('Kaggle login successful')

    def download(self, competition, files):
        if not self.login_browser:
            print('You are not logged in, please login with kaggle.login()')
            return

        if not isinstance(files, list):
            files = [files]
        for file_name in files:
            self.download_competition_file(competition, file_name, self.login_browser)

    def get_login_browser(self, username, password):

        pickle_path = os.path.join('browser.pickle')
        login_url = 'https://www.kaggle.com/account/login'
        browser = Browser()

        login_page = browser.get(login_url)
        login_form = login_page.soup.select("#login-account")[0]
        login_form.select("#UserName")[0]['value'] = username
        login_form.select("#Password")[0]['value'] = password
        login_result = browser.submit(login_form, login_page.url)
        if login_result.url == login_url:
            error = (login_result.soup
                    .select('#standalone-signin .validation-summary-errors')[0].get_text())
            print('There was an error logging in: ' + error)
            sys.exit(1)

        return browser

    def download_competition_file(self, competition, file_name, browser):

        print('Downloading %s' % file_name)
        url = 'https://www.kaggle.com/c/%s/download/%s' % (competition, file_name)
        res = browser.get(url, stream=True)

        total_size = int(res.headers.get('content-length', 0)); 

        if res.status_code != 200:
            print('error downloading %s' % file_name)
            return

        file_name = os.path.basename(url)

        pbar = tqdm(total=total_size, unit='B', unit_scale=True)
        chunk_size = 32 * 1024

        with open(file_name, 'wb') as file_handle:
            for data in res.iter_content(chunk_size):
                file_handle.write(data) 
                pbar.update(chunk_size)
                 

        print('%s downloaded' % file_name)
        settings.record_file_download(file_name)