import sys
import os
import pickle
import re
from .settings import settings

from mechanicalsoup import Browser

if settings.IS_IPYTHON:
    from tqdm import tqdm_notebook as tqdm
else:
    from tqdm import tqdm

class Kaggle():
    def __init__(self):
        self.login_browser = None

    def login(self, username, password):
        if not self.login_browser:
            self.login_browser = self.__get_login_browser(username, password)
            print('Kaggle login successful')

    def download(self, competition, files, cache=False):
        if not self.login_browser:
            print('Please log in to Kaggle with catalearn.kaggle.login()')
            return

        if not isinstance(files, list):
            files = [files]
        for file_name in files:
            cache_path = self.__maybe_get_cache_path(file_name)
            if cache_path:
                os.rename(cache_path, file_name)
                print('Using cached %s' % file_name)
                success = True
            else:
                success = self.__download_competition_file(competition, file_name, self.login_browser)
            if success: 
                settings.record_file_download(file_name, cache)


    def __maybe_get_cache_path(self, file_name):
        if not settings.SERVER or not settings.CACHE_PATH:
            return None

        all_cached = os.listdir(settings.CACHE_PATH)
        if file_name in all_cached:
            return os.path.join(settings.CACHE_PATH, file_name)

    def __get_login_browser(self, username, password):

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

    def __download_competition_file(self, competition, file_name, browser):

        url = 'https://www.kaggle.com/c/%s/download/%s' % (competition, file_name)
        res = browser.get(url, stream=True)

        total_size = int(res.headers.get('content-length', 0)); 

        if res.status_code != 200:
            print('error downloading %s' % file_name)
            return False

        file_name = os.path.basename(url)

        pbar = tqdm(total=total_size, unit='B', unit_scale=True, desc=file_name)
        chunk_size = 32 * 1024

        with open(file_name, 'wb') as file_handle:
            for data in res.iter_content(chunk_size):
                file_handle.write(data) 
                pbar.update(chunk_size)

        return True