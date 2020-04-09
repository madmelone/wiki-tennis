# Name:     ATP Player TouneyWins
# Author:   Michael Frey
# Version:  0.1
# Date:     20-03-2020
# Content:  Sets project wide variables

countryformat = 'ja'

#Secret Key for Flask require
import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'MiKa200816'