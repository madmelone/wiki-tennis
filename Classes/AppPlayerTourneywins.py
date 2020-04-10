# Name:     ATP Player TouneyWins
# Author:   Michael Frey
# Version:  0.1
# Date:     20-03-2020
# Content:  Returns the tournament wins of a player on the ATP Tour
# Apps:     - GetTournamentWins(ATPID, Matchtype="Singles") - Returns List of List of Information on Tournament wins by a player in a matchtype
#           - PrintTournamentWins(ListTournamentWins, Matchtype = "Singles") - Writes the Tournament Wins to a file in local output format

#Settings
mintourneytier = 3
excludedtourney = ['World Team Cup', 'World Team Championship']
filename = 'tournament.txt'

#List of imports
from Settings import countryformat
from ClassLocalization import *
from ClassSupportFunctions import *
import requests
from bs4 import BeautifulSoup
import os


def GetTourneylevel(filepath, TourneyName):
    if 'Olympics' in str(TourneyName):
        return 'olmypics'
    else:
        filename = os.path.basename(filepath)
        level = filename.split('_',2)
        if level[0] == 'nitto':
            return 'tourfinals'
        else:
            return level[1]

def GetTourneyTier(tourneylevel):
    TourneyTier = {'itf':1, 'challenger':2, '250':3, '500':3, 'atp':3, 'atpwt':3, '1000s':4, 'grandslam':5, 'olmypics':5, 'tourfinals':5}
    return TourneyTier[tourneylevel]

def LocalOutputFormat(TournamentInformation, format=countryformat):
    ResultList = []
    if format == 'de':
        #Print start of row and apply potential color coding
        ResultList.append(LocalTourneyColorFormat(TournamentInformation[7]))
        #Print tournament win number
        ResultList.append('| ' + str(TournamentInformation[0]) + '.')
        #Print tournament date
        ResultList.append('| ' + str(LocalDateFormat(TournamentInformation[10], format)))
        #Print tournament location
        ResultList.append('| ' + str(TournamentInformation[5]))
        #Print tournament surface
        ResultList.append('| ' + str(LocalSurfaceFormat(TournamentInformation[11], TournamentInformation[12], format)))
        #Print opponent
        ResultList.append('| {{' + str(TournamentInformation[1]) + '|' + str(TournamentInformation[2]) + '|' + str(TournamentInformation[2]) + '}}')
        #Print result
        ResultList.append('| ' + str(LocalMatchResultFormat(TournamentInformation[4], format)))
        ResultList.append('')
        #Join list
        OutputList = ('\n'.join(ResultList))
        return (OutputList)
    else:
        return string

def GetATPTournamentWins(ATPID, Matchtype):
    # - ATP-ID from Player-Profile, e.g. H355 for Tommy Haas
    # - Matchtype either Singles (standard) or Doubles
    ListReturn = []
    n = 0

    #Open ATP activity website
    url = 'https://www.atptour.com/en/players/-/' + ATPID + '/player-activity?year=all&matchType=' + Matchtype
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")

    #Read tournaments
    tournaments = soup.findAll("table", { "class" : "mega-table" })

    #Find all tournament finals
    finals = soup.find_all("td", string="Finals")

    #Read finals match information
    for i in range(len(finals)):
        PositionOpponentrank = finals[i].findNext('td')
        PositionOpponentcountry = PositionOpponentrank.findNext('a', { "class" : "mega-player-flag"})
        PositionOpponent1 = PositionOpponentrank.findNext('td').contents[0]
        PositionOpponent2 = PositionOpponent1.findNext('a', { "class" : "mega-player-name"})
        Winloss = str(PositionOpponent2.findNext('td').contents[0]).strip()

        #Get details in case tournament was won
        if Winloss == "W":

            #Get opponent details
            OpponentCountrycode = GetCountrycode(PositionOpponentcountry.findNext('img')['src'])
            OpponentName = PositionOpponent2.contents[0].strip()
            OpponentID = PositionOpponent2['href'].split('/')[4].strip()

            #Get match result
            PositionMatchResult = PositionOpponent2.findNext('a')

            # Clean MatchResult and tie-break results
            if len(PositionMatchResult.contents) > 1:
                templist = []
                for i in range(len(PositionMatchResult.contents)):
                    templist.append(str(PositionMatchResult.contents[i]).strip(',[]\',').rstrip())
                MatchResult = (''.join(templist))
            else:
                MatchResult = str(PositionMatchResult.contents).strip(',[]\',').rstrip()

            #Get tournament level (part 1, continues after tournament name)
            PositionTourneyLevel1 = PositionOpponentrank.findPrevious('td', { "class" : "tourney-badge-wrapper"})
            PositionTourneyLevel2 = PositionTourneyLevel1.findNext('img')['src']

            #Get tournament name and location
            PositionTourneyName = PositionTourneyLevel1.findNext('a', { "class" : "tourney-title"})
            TourneyName = PositionTourneyName.contents[0].strip()
            TourneyID = PositionTourneyName['href'].split('/')[4].strip()
            TourneyLocation = PositionTourneyLevel1.findNext('span', { "class" : "tourney-location"}).contents[0].strip()

            #Get tournament level (part 2, continued from before tournament name
            TourneyLevel = GetTourneylevel(PositionTourneyLevel2, TourneyName)
            TourneyTier = GetTourneyTier(TourneyLevel)

            #Get tournament finals day
            PositionTourneyweek = PositionTourneyLevel1.findNext('span', {"class": "tourney-dates"})
            TourneyWeek = PositionTourneyweek.contents[0].strip()
            TourneyWeek2 = TourneyWeek.replace('.','-')
            TourneyDate = TourneyWeek2[-10:]

            #Get tournament surface
            PositionTourneySurface1 = PositionTourneyweek.findNext('div', {"class": "icon-court image-icon"})
            PositionTourneySurface2 = PositionTourneySurface1.findNext('div', {"class": "info-area"})
            TourneySurface = PositionTourneySurface2.findNext('span', {"class": "item-value"}).contents[0].strip()
            TourneySurfaceInOut = PositionTourneySurface2.findNext('div', {"class": "item-details"}).contents[0].strip()

            #Return values if tournament minimum level is reached AND is not tournament is not World Team Cup
            if int(TourneyTier) >= mintourneytier and TourneyName not in excludedtourney:
                ListReturn.append([OpponentCountrycode, OpponentName, OpponentID, MatchResult, TourneyName, TourneyID, TourneyLevel, TourneyTier, TourneyLocation, TourneyDate, TourneySurface, TourneySurfaceInOut])

    #Order tournaments in reverse to oldest to newest
    ListReturn.reverse()

    #Add number to each tournament win
    for i in range(len(ListReturn)):
        n = n +1
        ListReturn[i].insert(0, str(n))

    #Return list of tournament wins
    return ListReturn

def PrintTournamentWins(ListTournamentWins, Matchtype = "Singles"):
    FileOutput = open(filename, "a")
    #Write Header
    OutputHeader = '==== Turniersiege ==== \n{| class=\"wikitable\"\n|- style=\"background:#EEEEEE;\"\n! Nr.\n! Datum\n! Turnier\n! Belag\n! Finalgegner\n! Ergebnis\n'
    FileOutput.write(OutputHeader)
    #Write tournament wins
    for i in range(len(ListTournamentWins)):
        FileOutput.writelines(LocalOutputFormat(ListTournamentWins[i]))
    #Write Footer and close file
    FileOutput.write('|}')
    FileOutput.close()
    #print("File written")

def GetTournamentWins(RankingOrg, PlayerID, Matchtype="Singles"):
    if RankingOrg == 'atp':
        return GetATPTournamentWins(PlayerID, Matchtype)
    #elif RankingOrg == 'wta':
    #    return GetWTATournamentWins(PlayerID, Matchtype)
    #elif RankingDate =='itf':
    #    return GetITFTournamentWins(PlayerID, Matchtype)
    else:
        exit('Incorrect Ranking Organisation')

def TournamentWinsOutput(ListTournamentWins, language):
    # Write Header
    OutputHeader = '==== Turniersiege ==== \n{| class=\"wikitable\"\n|- style=\"background:#EEEEEE;\"\n! Nr.\n! Datum\n! Turnier\n! Belag\n! Finalgegner\n! Ergebnis\n'
    # Write tournament wins
    OutputPlayer = []
    for i in range(len(ListTournamentWins)):
        OutputPlayer.append(LocalOutputFormat(ListTournamentWins[i], language))
    OutputList = ('\n'.join(OutputPlayer))

    OutputClose = '|}'
    Output = OutputHeader + OutputList + OutputClose
    return Output.replace("\n", "<br />").replace("<br /><br />", "<br />")