# Name:     Player World Ranking
# Author:   Michael Frey
# Version:  0.21
# Date:     05-04-2020
# Content:  Returns the tennis world rankings

# -*- coding: utf-8 -*-

#Internal imports
from ClassSupportFunctions import *
from ClassLocalization import *
from ClassWikidata import *

#External imports
import requests
from Settings import countryformat
from bs4 import BeautifulSoup

def LocalRankingFormat(RankingInformation, format=countryformat):
    ResultList = []
    if format == 'de':
        #Print ranking number number & player name including link
        ResultList.append('|- \n| ' \
                        + str(RankingInformation[0]) \
                        + '\n| {{' \
                        + str(RankingInformation[1]) \
                        + '|' \
                        + str(RankingInformation[3]) \
                        + '|' \
                        + str(RankingInformation[2]) \
                        + '}}\n|' \
                        + '<small>')
    elif format == 'ja':
        #Print ranking number number & player name including link
        ResultList.append('|- \n| ' \
                        + str(RankingInformation[0]) \
                        + '\n| {{flagicon|' \
                        + str(RankingInformation[1]) \
                        + '}} [[' \
                        + str(RankingInformation[3]) \
                        + '|' \
                        + str(RankingInformation[2]) \
                        + ']]\n|' \
                        + '<small>')
    else:
        return string

    # Print sitelinks
    sitelinks = RankingInformation[4]
    if sitelinks == '-':
        ResultList.append('-</small>')
    else:
        for i in range(len(sitelinks)):
            ResultList.append('([[:' + str(sitelinks[i][0]) + ':' + str(sitelinks[i][1]) + '|' + str(sitelinks[i][0]) + ']]) ')
        ResultList.append('</small>')
    # Join list
    OutputList = ('\n'.join(ResultList))
    return (OutputList)


def GetWorldRanking(RankingOrg = 'atp', MatchType = 'singles', RankingCut = '100', language=countryformat, RankingDate= ''):
    if RankingOrg == 'atp':
        return GetATPWorldRanking(MatchType, RankingCut, language, RankingDate)
    elif RankingOrg == 'wta':
        return GetWTAWorldRanking(MatchType, RankingCut, language, RankingDate)
    elif RankingDate =='itf':
        return GetITFWorldRanking(MatchType, RankingCut, language, RankingDate)
    else:
        exit('Incorrect Ranking Organisation')

def GetATPWorldRanking(MatchType= 'singles', RankingCut = 10, language = countryformat, RankingDate = ''):

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
    ListIDs = []
    ListReturn = []

    PositionRank = soup.findAll("td", {"class": "rank-cell"})
    for i in range(len(PositionRank)):
        #Get Player Rank
        #Erase T fot tied so that the ranking may later be translated to an integer
        temp = str(PositionRank[i].get_text()).strip()
        if 'T' in temp:
            PlayerRank = temp[:-1]
        else:
            PlayerRank = temp

        #Get ATP ID of each player
        PositionCountry = PositionRank[i].findNext('td', {"class": "country-cell"})
        PositionName1 = PositionCountry.findNext('td', {"class": "player-cell"})
        PositionName2 = PositionName1.findNext('a')
        PlayerATPID = PositionName2['href'].split('/')[4].strip().upper()
        ListIDs.append(PlayerATPID)
    #Format list to string
    InputIDs = '\"' + '\"\n\"'.join(ListIDs) + '\"'
    try:
        #Derive Player information from Wikidata by ATP-ID
        WikidataPlayerInfo = WikidataGetPlayerInfo('atp', InputIDs, language)

        for n in range(len(WikidataPlayerInfo)):
            Sitelinks = []
            PlayerRank = str(WikidataPlayerInfo[n][2])
            #PlayerQID = str(WikidataPlayerInfo[n][0])
            PlayerName = str(WikidataPlayerInfo[n][3])
            PlayerLemma = str(WikidataPlayerInfo[n][4])
            PlayerCountry = str(WikidataPlayerInfo[n][5])
            Sitelinks = WikidataPlayerInfo[n][6]
            ListReturn.append([int(PlayerRank), PlayerCountry, PlayerName, PlayerLemma, Sitelinks])
    except:
        # If Wikidata query does not work, get information from ATP website
        for m in range(len(PositionRank)):
            # Get Player Rank
            PlayerRank = str(m + 1)
            PositionCountry = PositionRank[m].findNext('td', {"class": "country-cell"})
            PositionName1 = PositionCountry.findNext('td', {"class": "player-cell"})
            PositionName2 = PositionName1.findNext('a')
            PlayerName = PositionName2.contents[0].strip()
            PlayerLemma = PlayerName
            PlayerCountry = GetCountrycode(PositionCountry.findNext('img')['src'])
            Sitelinks = '-'
            ListReturn.append([int(PlayerRank), PlayerCountry, PlayerName, PlayerLemma, Sitelinks])
    #Add information from ATP website if no results found so far
    # First build a set with all ranking numbers from 1 to RankingCut
    SetTotal = set()
    for j in range(RankingCut):
        SetTotal.add(j+1)
    #Second build a set with all ranking numbers that have player information
    SetWD = set()
    for k in range(len(WikidataPlayerInfo)):
        SetWD.add(int(ListReturn[k][0]))
    #Get differences from sets which is the ranking numbers of players with no information provided
    SetTotal.difference_update(SetWD)
    #Get information on the outstanding players
    for l in range(len(PositionRank)):
        #Erase T for tied to be able to translate string to an integer
        if 'T' in str(PositionRank[l].get_text()).strip():
            temp = str(PositionRank[l].get_text()).strip()[:-1]
        else:
            temp = str(PositionRank[l].get_text()).strip()
        #Run through outstanding player information
        if int(temp) in SetTotal:
            PlayerRank = str(PositionRank[l].get_text()).strip()
            PositionCountry = PositionRank[l].findNext('td', {"class": "country-cell"})
            PositionName1 = PositionCountry.findNext('td', {"class": "player-cell"})
            PositionName2 = PositionName1.findNext('a')
            PlayerName = PositionName2.contents[0].strip()
            PlayerLemma = PlayerName
            PlayerCountry = GetCountrycode(PositionCountry.findNext('img')['src'])
            Sitelinks = '-'
            #Insert information into ListReturn at the ranking position
            ListReturn.insert(int(PlayerRank) + 1, [int(PlayerRank), PlayerCountry, PlayerName, PlayerLemma, Sitelinks])
    ListReturn.sort(key=lambda x: x[0])
    return ListReturn

def GetWTAWorldRanking(MatchType= 'singles', RankingCut = 100, language = countryformat, RankingDate = ''):
    print(language)
    #Check input parameters
    #MatchType can only be singles or doubles
    if MatchType not in ['singles', 'doubles']:
        exit('Incorrect MatchType (only \'singles\' or \'doubles\')')
    InputMatchType = str(MatchType)

    #RankingCut maximum at 5000 by WTA website
    if int(RankingCut) > 5000:
        exit('Maximum allowed ranking range at 5,000')
    else:
        InputRankingCut = str(RankingCut)

    #Set URL for really live scenarios outside testing
    #url = 'https://www.wtatennis.com/rankings/' + InputMatchType
    #Open website
    #req = requests.get(url)
    #soup = BeautifulSoup(req.text, "html.parser")

    #Set URL just for internal testing purposes to a downloaded html file
    if MatchType == 'singles':
        f = open('wtatest.html', 'r')
    elif MatchType == 'doubles':
        f = open('doubles.html', 'r')
    s = f.read()
    soup = BeautifulSoup(s, "html.parser")

    #Read ranking and player information
    ListIDs = []
    ListReturn = []

    PositionRank = soup.findAll("span", {"class": "rankings__rank"})
    for i in range(len(PositionRank)):
        #Get Player Rank
        PlayerRank = str(PositionRank[i].get_text()).strip()
        #Get WTA ID of each player
        PositionPlayerID = PositionRank[i].findNext('a')
        PlayerID = PositionPlayerID['href'].split('/')[4].strip() + '/' + PositionPlayerID['href'].split('/')[5].strip()
        ListIDs.append(PlayerID)
    #Format list to string
    InputIDs = '\"' + '\"\n\"'.join(ListIDs) + '\"'

    try:
        #Derive Player information from Wikidata by ATP-ID
        WikidataPlayerInfo = WikidataGetPlayerInfo('wta', InputIDs, language)

        for n in range(len(WikidataPlayerInfo)):
            Sitelinks = []
            PlayerRank = str(WikidataPlayerInfo[n][2])
            #PlayerQID = str(WikidataPlayerInfo[n][0])
            PlayerName = str(WikidataPlayerInfo[n][3])
            PlayerLemma = str(WikidataPlayerInfo[n][4])
            PlayerCountry = str(WikidataPlayerInfo[n][5])
            Sitelinks = WikidataPlayerInfo[n][6]
            ListReturn.append([int(PlayerRank), PlayerCountry, PlayerName, PlayerLemma, Sitelinks])
    except:
        # If Wikidata query does not work, get information from WTA website
        for m in range(len(PositionRank)):
            # Get Player Rank
            PlayerRank = str(m + 1)
            PositionName = PositionPlayerID.findNext('a', {"class": "rankings__player-link"})
            PlayerName = PositionName.contents[0].strip()
            PlayerLemma = PlayerName
            PositionCountry = PositionPlayerID.findNext('img', {"class": "flag rankings__flag"})
            PlayerCountry = GetCountrycode(PositionCountry['src'])
            Sitelinks = '-'
            ListReturn.append([int(PlayerRank), PlayerCountry, PlayerName, PlayerLemma, Sitelinks])

    #Add information from WTA website if no results found so far
    # First build a set with all ranking numbers from 1 to RankingCut
    SetTotal = set()
    for j in range(RankingCut):
        SetTotal.add(j+1)
    #Second build a set with all ranking numbers that have player information
    SetWD = set()
    for k in range(len(WikidataPlayerInfo)):
        SetWD.add(int(ListReturn[k][0]))
    #Get differences from sets which is the ranking numbers of players with no information provided
    SetTotal.difference_update(SetWD)
    #Get information on the outstanding players
    for l in range(len(PositionRank)):
        if int((str(PositionRank[l].get_text()).strip())) in SetTotal:
            PlayerRank = str(PositionRank[l].get_text()).strip()
            PositionName = PositionRank[l].findNext('a', {"class": "rankings__player-link"})
            PlayerName = PositionName.contents[0].strip()
            PlayerLemma = PlayerName
            PositionCountry = PositionRank[l].findNext('img', {"class": "flag rankings__flag"})
            PlayerCountry = GetCountrycode(PositionCountry['src'])
            Sitelinks = '-'
            # Insert information into ListReturn at the ranking position
            ListReturn.insert(int(PlayerRank) + 1, [int(PlayerRank), PlayerCountry, PlayerName, PlayerLemma, Sitelinks])
    ListReturn.sort(key=lambda x: x[0])
    return ListReturn

def GetITFWorldRanking(MatchType= 'singles', RankingCut = 100, RankingDate = ''):
    print('ITF')
    print(MatchType)
    print(RankingCut)
    print(RankingDate)

def PrintRanking(RankingList, RankingOrg, Matchtype, RankingCut, Language, RankingDate):
    filename = "worldranking.txt"
    FileOutput = open(filename, 'a', encoding='utf-8')

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
    OutputTableHeader = '\n\n\n{| class="wikitable"\n|+\n! style="width: 5em" |#\n! style="width: 30em" | Player\n!Other Languages\n'
    FileOutput.write(OutputTableHeader)

    #Write world ranking table contents
    for i in range(len(RankingList)):
        FileOutput.writelines(LocalRankingFormat(RankingList[i], Language))

    # Write Footer and close file
    FileOutput.write('|}')
    FileOutput.close()
    print("File written")

def RankingOutput(RankingList, RankingOrg, Matchtype, RankingCut, Language, RankingDate):
    OutputHeader = '=== World Ranking ===\n'
    OutputMeta = '\n\n{| class=\"wikitable\"\n|+\n!Item\n!Value\n|-\n| RankingOrg\n|' \
                + RankingOrg \
                + '\n|-\n| MatchType\n|'\
                + Matchtype \
                + '\n|-\n| RankingCut\n|'\
                + str(RankingCut) \
                + '\n|-\n| RankingDate\n|'\
                + RankingDate \
                + '\n|}'
    OutputTableHeader = '\n\n\n{| class="wikitable"\n|+\n! style="width: 5em" |#\n! style="width: 30em" | Player\n!Other Languages\n'

    #Write world ranking table contents
    OutputPlayer = []
    for i in range(len(RankingList)):
        OutputPlayer.append(LocalRankingFormat(RankingList[i], Language))
    OutputList = ('\n'.join(OutputPlayer))
    OutputClose = '\n|}'
    Output = OutputHeader + OutputMeta + OutputTableHeader + OutputList + OutputClose
    return Output
