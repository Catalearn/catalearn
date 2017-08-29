from bs4 import BeautifulSoup
import re
import pkg_resources
import requests

def isLatestVersion():
    currentVersion = pkg_resources.get_distribution('catalearn').version

    r = requests.get('https://pypi.python.org/simple/catalearn/')
    soup = BeautifulSoup(r.text, "html5lib")
    allVersions = []
    for link in soup.find_all('a'):
        text = link.get_text()
        result = re.search('catalearn-(.+)-py3-none-any\.whl', text)
        if result:
            allVersions.append(result.group(1))

    allVersions.sort()
    latestVersion = allVersions[-1]

    return currentVersion == latestVersion