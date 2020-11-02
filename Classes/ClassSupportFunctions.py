import os
import json
import requests
import time
from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.firefox.options import Options as FirefoxOptions

def GetCountrycode(filepath):
    filename = os.path.basename(filepath)
    return filename[0:3].upper()

def GetSoup(path, headers):
    if headers == True: # want soup for html in path
        return BeautifulSoup(path, "html.parser")
    elif headers == False: # want request only
        return requests.get(path)
    elif headers == "json":
        return json.loads(requests.get(path).text)
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

def Dedupe(x):
    return list(dict.fromkeys(x))

# def GetSoupSelenium(url):
#     options = FirefoxOptions()
#     options.add_argument("--headless")
#     driver = webdriver.Firefox(options=options)
#     driver.get(url)
#     time.sleep(5) # wait for JavaScript to load
#     source = driver.page_source
#     soup = get_soup(source, True)

def LowerName(name):
    return name.lower().replace("-", "").replace(" ", "").replace(".", "")
