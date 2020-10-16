import os

def GetCountrycode(filepath):
    filename = os.path.basename(filepath)
    return filename[0:3].upper()