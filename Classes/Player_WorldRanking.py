# Name:     Player World Ranking
# Author:   Michael Frey
# Version:  0.2
# Date:     29-03-2020
# Content:  Returns the tennis world rankings

from ClassLocalization import *
import requests
from ClassSupportFunctions import *
from Settings import countryformat
from bs4 import BeautifulSoup

def LocalRankingFormat(RankingInformation, format=countryformat):
    ResultList = []
    if format == 'de':
        #Print ranking number number
        ResultList.append('|- \n| ' \
                        + str(RankingInformation[0]) \
                        + '\n| {{' \
                        + str(RankingInformation[1]) \
                        + '|' \
                        + str(RankingInformation[2]) \
                        + '|' \
                        + str(RankingInformation[2]) \
                        + '}}\n|' \
                        + '<small>in progress</small>')
        ResultList.append('')
        #Join list
        OutputList = ('\n'.join(ResultList))
        return (OutputList)
    else:
        return string

def GetWorldRanking(RankingOrg = 'atp', MatchType = 'singles', RankingCut = '100', RankingDate= ''):
    if RankingOrg == 'atp':
        return GetATPWorldRanking(MatchType, RankingCut, RankingDate)
    elif RankingOrg == 'wta':
        return GetWTAWorldRanking(MatchType, RankingCut, RankingDate)
    elif RankingDate =='itf':
        return GetITFWorldRanking(MatchType, RankingCut, RankingDate)
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
    #Open website
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")

    #Read ranking and player information
    ListReturn = []
    PositionRank = soup.findAll("td", {"class": "rank-cell"})
    for i in range(len(PositionRank)):
        #Get Player Rank
        PlayerRank = str(PositionRank[i].get_text()).strip()
        #Get Player Country Code
        PositionCountry = PositionRank[i].findNext('td', {"class": "country-cell"})
        PlayerCountry = GetCountrycode(PositionCountry.findNext('img')['src'])
        #Get Player Name
        PositionName1 = PositionCountry.findNext('td', {"class": "player-cell"})
        PositionName2 = PositionName1.findNext('a')
        PlayerName = PositionName2.contents[0].strip()
        PlayerATPID = PositionName2['href'].split('/')[4].strip()

        ListReturn.append([PlayerRank, PlayerCountry, PlayerName, PlayerATPID])
    return ListReturn

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

def PrintRanking(RankingList, RankingOrg, Matchtype, RankingCut, RankingDate):
    filename = "worldranking.txt"
    FileOutput = open(filename, "a")
    print(RankingList)

    # Write Header
    OutputHeader = '=== World Ranking ===\n'
    FileOutput.write(OutputHeader)

    # Write meta information
    OutputMeta = '\n\n{| class=\"wikitable\"\n|+\n!Item\n!Value\n|-\n| RankingOrg\n|' \
                + RankingOrg \
                + '\n|-\n| MatchType\n|'\
                + Matchtype \
                + '\n|-\n| RankingCut\n|'\
                + str(RankingCut) \
                + '\n|-\n| RankingDate\n|'\
                + RankingDate \
                + '\n|}'
    FileOutput.write(OutputMeta)

    #Write world ranking table header
    OutputTableHeader = '\n\n\n{| class="wikitable"\n|+\n!#\n!Player\n!Other Languages\n'
    FileOutput.write(OutputTableHeader)

    #Write world ranking table contents
    for i in range(len(RankingList)):
        FileOutput.writelines(LocalRankingFormat(RankingList[i]))

    # Write Footer and close file
    FileOutput.write('|}')
    FileOutput.close()
    print("File written")

#a= GetWorldRanking('atp', 'singles', 500, '2020-03-16')
#PrintRanking(a, 'atp', 'singles', 500, '2020-03-16')