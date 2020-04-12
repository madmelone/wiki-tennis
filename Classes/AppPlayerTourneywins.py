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

def LocalTableFormat(format, type):
    if format == 'de':
        if type == 'singles':
            Output = '==== Turniersiege ==== \n{| class=\"wikitable\"\n|- style=\"background:#EEEEEE;\"\n! Nr.\n! Datum\n! Turnier\n! Belag\n! Finalgegner\n! Ergebnis\n'
        elif type == 'doubles':
            Output = '==== Turniersiege ==== \n{| class=\"wikitable\"\n|- style=\"background:#EEEEEE;\"\n! Nr.\n! Datum\n! Turnier\n! Belag\n! Partner\n! Finalgegner\n! Ergebnis\n'
    else:
        Output = '==== Turniersiege ==== \n{| class=\"wikitable\"\n|- style=\"background:#EEEEEE;\"\n! Nr.\n! Datum\n! Turnier\n! Belag\n! Finalgegner\n! Ergebnis\n'
    return Output

def LocalTourneyFormat(TournamentInformation, format, type):
    ResultList = []
    if format == 'de':

        #ListReturn.append(
        #    [0#,1Opponent1Countrycode, 2Opponent1Name, 3Opponent1ID, 4MatchResult, 5TourneyName, 6TourneyID, 7TourneyLevel,
        #     8TourneyTier, 9TourneyLocation, 10TourneyDate, 11TourneySurface, 12TourneySurfaceInOut, 13Opponent2Countrycode,
        #     14Opponent2Name, O15pponent2ID, 16PartnerCountrycode, 17PartnerName, 18PartnerID])
        if type == 'singles':
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
            #Join list
            OutputList = ('\n'.join(ResultList))
        elif type == 'doubles':
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
            # Print partner
            ResultList.append('| {{' + str(TournamentInformation[16]) + '|' + str(TournamentInformation[17]) + '|' + str(TournamentInformation[17]) + '}}')
            #Print opponents
            ResultList.append('| {{' + str(TournamentInformation[1]) + '|' + str(TournamentInformation[2]) + '|' + str(TournamentInformation[2]) + '}} <br /> {{' + str(TournamentInformation[13]) + '|' + str(TournamentInformation[14]) + '|' + str(TournamentInformation[14]) + '}}')
            #Print result
            ResultList.append('| ' + str(LocalMatchResultFormat(TournamentInformation[4], format)))
            #Join list
            OutputList = ('\n'.join(ResultList))
        return (OutputList)
    else:
        return TournamentInformation

def GetTournamentWins(RankingOrg, PlayerID, MatchType, MinimumTier = mintourneytier):
    if RankingOrg == 'atp':
        return GetATPTournamentWins(PlayerID, MatchType, MinimumTier)
    elif RankingOrg == 'wta':
        return GetWTATournamentWins(PlayerID, MatchType, MinimumTier)
    elif RankingOrg =='itf':
        return GetITFTournamentWins(PlayerID, MatchType, MinimumTier)
    else:
        exit('Incorrect Ranking Organisation')

def GetATPTournamentWins(ATPID, Matchtype, MinimumTier = mintourneytier):
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
        PositionOpponents = finals[i].findNext('td')
        PositionOpponent1Country = PositionOpponents.findNext('a', {"class" : "mega-player-flag"})
        PositionOpponent1Name = PositionOpponents.findNext('td').contents[0].findNext('a', { "class" : "mega-player-name"})
        Winloss = str(PositionOpponent1Name.findNext('td').contents[0]).strip()

        #Get details in case tournament was won
        if Winloss == "W":
            #Get details for opponent 1 (in singles and doubles)
            Opponent1Countrycode = GetCountrycode(PositionOpponent1Country.findNext('img')['src'])
            Opponent1Name = PositionOpponent1Name.contents[0].strip()
            Opponent1ID = PositionOpponent1Name['href'].split('/')[4].strip()

            #Get details for opponent 2 (in doubles)
            Opponent2Countrycode = ''
            Opponent2Name = ''
            Opponent2ID = ''
            if Matchtype == 'doubles':
                PositionOpponent2Country = PositionOpponent1Country.findNext('a', {"class": "mega-player-flag"})
                PositionOpponent2Name = PositionOpponent1Name.findNext('a', { "class": "mega-player-name"})
                Opponent2Countrycode = GetCountrycode(PositionOpponents.findNext('img').findNext('img')['src'])
                Opponent2Name = PositionOpponent2Name.contents[0].strip()
                Opponent2ID = PositionOpponent2Name['href'].split('/')[4].strip()

            #Get match result
            PositionMatchResult = PositionOpponent2Name.findNext('a')
            # Clean MatchResult and tie-break results
            if len(PositionMatchResult.contents) > 1:
                templist = []
                for i in range(len(PositionMatchResult.contents)):
                    templist.append(str(PositionMatchResult.contents[i]).strip(',[]\',').rstrip())
                MatchResult = (''.join(templist))
            else:
                MatchResult = str(PositionMatchResult.contents).strip(',[]\',').rstrip()
            #Get tournament level (part 1, continues after tournament name)
            PositionTourneyLevel1 = PositionOpponents.findPrevious('td', {"class" : "tourney-badge-wrapper"})
            PositionTourneyLevel2 = PositionTourneyLevel1.findNext('img')['src']
            #Get tournament name and location
            PositionTourneyName = PositionTourneyLevel1.findNext('a', { "class" : "tourney-title"})
            PositionTourneyNameFallback = PositionTourneyLevel1.findNext('span', {"class": "tourney-title"})
            try:
                TourneyName = PositionTourneyName.contents[0].strip()
                TourneyID = PositionTourneyName['href'].split('/')[4].strip()
            except AttributeError:
                TourneyName = PositionTourneyNameFallback.contents[0].strip()
                TourneyID = ''
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

            #Get details for doubles partner
            PartnerCountrycode = ''
            PartnerName = ''
            PartnerID = ''
            if Matchtype == 'doubles':
                PositionPartner1 = PositionTourneySurface2.findNext('div', {"class": "activity-tournament-caption"})
                PositionPartner2 = PositionPartner1.findNext('a')
                #Only temporary fix until Wikidata implementation ready
                PartnerCountrycode = 'WELT'
                PartnerName = PositionPartner2.contents[0].strip()
                PartnerID = PositionPartner2['href'].split('/')[4].strip()

            #Return values if tournament minimum level is reached AND is not tournament is not World Team Cup
            if int(TourneyTier) >= MinimumTier and TourneyName not in excludedtourney:
                ListReturn.append([Opponent1Countrycode, Opponent1Name, Opponent1ID, MatchResult, TourneyName, TourneyID, TourneyLevel, TourneyTier, TourneyLocation, TourneyDate, TourneySurface, TourneySurfaceInOut, Opponent2Countrycode, Opponent2Name, Opponent2ID, PartnerCountrycode, PartnerName, PartnerID])

    #Order tournaments in reverse to oldest to newest
    ListReturn.reverse()

    #Add number to each tournament win
    for i in range(len(ListReturn)):
        n = n +1
        ListReturn[i].insert(0, str(n))

    #Return list of tournament wins
    return ListReturn

def GetWTATournamentWins(PlayerID, MatchType, MinimumTier):
    print('WTA')
    print(PlayerID)
    print(MatchType)
    print(MinimumTier)

def GetITFTournamentWins(PlayerID, MatchType, MinimumTier):
    print('ITF')
    print(PlayerID)
    print(MatchType)
    print(MinimumTier)

def PrintTournamentWins(ListTournamentWins, Matchtype = "Singles"):
    FileOutput = open(filename, "a")
    #Write Header
    OutputHeader = '==== Turniersiege ==== \n{| class=\"wikitable\"\n|- style=\"background:#EEEEEE;\"\n! Nr.\n! Datum\n! Turnier\n! Belag\n! Finalgegner\n! Ergebnis\n'
    FileOutput.write(OutputHeader)
    #Write tournament wins
    for i in range(len(ListTournamentWins)):
        FileOutput.writelines(LocalTourneyFormat(ListTournamentWins[i]))
    #Write Footer and close file
    FileOutput.write('|}')
    FileOutput.close()
    #print("File written")

def TournamentWinsOutput(ListTournamentWins, Language, MatchType):
    # Write Header
    OutputHeader = LocalTableFormat(Language, MatchType)
    # Write tournament wins
    OutputPlayer = []
    for i in range(len(ListTournamentWins)):
        OutputPlayer.append(LocalTourneyFormat(ListTournamentWins[i], Language, MatchType))
    OutputList = ('\n'.join(OutputPlayer))

    OutputClose = '\n|}'
    Output = OutputHeader + OutputList + OutputClose
    return Output