# Name:     Player World Ranking
# Author:   Michael Frey
# Version:  0.11
# Date:     22-03-2020
# Content:  Returns the tennis world rankings

from ClassLocalization import *
import requests
import datetime
from bs4 import BeautifulSoup

def GetWorldRanking(RankingOrg = 'atp', MatchType = 'singles', RankingCut = '100', RankingDate= ''):
    if RankingOrg == 'atp':
        GetATPWorldRanking(MatchType, RankingCut, RankingDate)
    elif RankingOrg == 'wta':
        GetWTAWorldRanking(MatchType, RankingCut, RankingDate)
    elif RankingDate =='itf':
        GetITFWorldRanking(MatchType, RankingCut, RankingDate)
    else:
        exit('Incorrect Ranking Organisation')

def GetATPWorldRanking(MatchType= 'singles', RankingCut = 100, RankingDate = ''):

    #Check input parameters
    #MatchType can only be singles or doubles
    if MatchType not in ['singles', 'doubles']:
        exit('Incorrect MatchType (only \'singles\' or \'doubles\')')
    InputMatchType = str(MatchType)

    #RankingCut maximum at 5000 by ATP website
    if int(RankingCut) > 5000:
        exit('Maximum allowed ranking range at 5,000')
    else:
        InputRankingCut = str(RankingCut)

    #Only certain ranking dates possible on ATP website - get them from the dropdown menu
    DateList = []
    #Find dropdown menu with available dates
    URLDateList = 'https://www.atptour.com/en/rankings/' + InputMatchType
    DateListRequest = requests.get(URLDateList)
    DateCheck = BeautifulSoup(DateListRequest.text, "html.parser")
    #Write list of all available dates
    AvailableDatesDropdown = DateCheck.find("ul", {"data-value": "rankDate"})
    DropdownValues = AvailableDatesDropdown.findAll("li")
    for i in range(len(DropdownValues)):
        Date = str(DropdownValues[i].contents[0]).strip().replace('.','-')
        DateList.append(Date)
    #Check whether RankingDate is an allowed date
    if RankingDate in DateList:
        InputRankingDate = str(RankingDate)
    else:
        exit('Wrong date')


    #Set URL
    url = 'https://www.atptour.com/en/rankings/' + InputMatchType + '?rankDate=' + InputRankingDate + '&rankRange=1-' + InputRankingCut
    print(url)
    #Open website
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")

    #Read ranking and player information
    ranks = soup.findAll("td", {"class": "rank-cell"})
    players = soup.findAll("td", {"class": "player-cell"})

def GetWTAWorldRanking(MatchType= 'singles', RankingCut = 100, RankingDate = ''):
    print('WTA')
    print(MatchType)
    print(RankingCut)
    print(RankingDate)


def GetITFWorldRanking(MatchType= 'singles', RankingCut = 100, RankingDate = ''):
    print('ITF')
    print(MatchType)
    print(RankingCut)
    print(RankingDate)


    #Set URL

GetWorldRanking('atp', 'singles', 10, '2020-01-20')