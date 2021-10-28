import os
import json
import requests
import time
from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.firefox.options import Options as FirefoxOptions
# from webdriver_manager.firefox import GeckoDriverManager

os.environ['WDM_LOG_LEVEL'] = '0' # silence webdriver_manager output

def GetCountrycode(filepath):
    filename = os.path.basename(filepath)
    return filename[0:3].upper()

def GetSoup(path, headers):
    if headers == True: # want soup for html in path
        return BeautifulSoup(path, "html.parser")
    elif headers == False: # want request only
        return requests.get(path)
    elif headers == "json":
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        return json.loads(requests.get(path, headers=headers).text)
    elif headers == {}:
        response = requests.get(path).text
    else:
        response = requests.get(path, headers=headers).text
    return BeautifulSoup(response, 'lxml')

def LoadJSON(path):
    try:
        with open(path, 'r') as fp:
            return json.load(fp)
    except FileNotFoundError:
        return {}

def SaveJSON(path, data):
    with open(path, 'w') as fp:
        json.dump(data, fp, sort_keys=True, indent=4)

def LoadFile(path):
    data = []
    if os.path.exists(path):
        with open(path, "r", encoding="ISO 8859-1") as infile:
            data = infile.readlines()
        data = [f.replace('\n', '') for f in data]
    return data if data != None else []

def SaveFile(path, data):
    with open(path, "wb") as outfile:
        data = [f.encode('utf-8') for f in data]
        outfile.write(("\n".encode('utf-8')).join(data))

def Dedupe(x):
    return list(dict.fromkeys(x))

def GetSoupSelenium(url, driver):
    if driver == None:
        options = FirefoxOptions()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options, executable_path=GeckoDriverManager().install())
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36")
    driver.get(url)
    time.sleep(2) # wait for JavaScript to load
    source = driver.page_source
    soup = GetSoup(source, True)
    return soup, driver

def GetSoupWayback(url):
    soup = GetSoup("http://web.archive.org/save/" + url, None)
    soup = GetSoup("https://web.archive.org/web/2030/" + url, None)
    print ("https://web.archive.org/web/2030/" + url)
    return soup

def LowerName(name):
    return name.lower().replace("-", "").replace(" ", "").replace(".", "")
