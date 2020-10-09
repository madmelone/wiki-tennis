import os
import json
import requests
from bs4 import BeautifulSoup

def GetCountrycode(filepath):
    filename = os.path.basename(filepath)
    return filename[0:3].upper()

def GetSoup(path, headers):
    if headers == True: # want soup for html in path
        return BeautifulSoup(path, "html.parser")
    elif headers == False: # want request only
        return requests.get(path)
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
