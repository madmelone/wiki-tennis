#Settings
mintourneytier = 3
excludedtourney = ['World Team Cup', 'World Team Championship']

#List of imports
from Settings import countryformat
from ClassLocalization import *
from ClassSupportFunctions import *
from ClassWikidata import WikidataGetPlayerInfoshort
import os
import pycountry


def GetTourneylevel(filepath, TourneyName):
    if 'Olympics' in str(TourneyName):
        return 'olmypics'
    elif 'Grand Slam Cup' in str(TourneyName):
        return 'tourfinals'
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
    elif format == 'nl':
        if type == 'singles':
            Output = '=== Enkelspel === \n{| class=\"wikitable\" style=\"line-height: 1.0\"\n|- bgcolor=\"#efefef\"\n!Nr. !! Datum !! Toernooi !! Ondergrond !! Tegenstander in finale !! Score !! Details\n|- bgcolor=\"#efefef\" align=\"center\"\n|colspan=\"7\"| \'\'\'Gewonnen finales\'\'\'\n'
        elif type == 'doubles':
            Output = '=== Dubbelspel  === \n{| class=\"wikitable\" style=\"line-height: 1.0\"\n|-\n! Nr. !! Datum !! Toernooi !! Ondergrond !! Partner !! Tegenstanders in finale !! Score !! Details\n|- bgcolor=\"#efefef\" align=\"center\"\n|colspan=\"8\"| \'\'\'Gewonnen finales herendubbel\'\'\'\n'
    else:
        Output = '==== Turniersiege ==== \n{| class=\"wikitable\"\n|- style=\"background:#EEEEEE;\"\n! Nr.\n! Datum\n! Turnier\n! Belag\n! Finalgegner\n! Ergebnis\n'
    return Output

def LocalTourneyFormat(TournamentInformation, format, type, result):
    ResultList = []
    OutputList = ''
    if format == 'de':

        #    [0#,1Opponent1Countrycode, 2Opponent1Name, 3Opponent1ID, 4MatchResult, 5TourneyName, 6TourneyID, 7TourneyLevel,
        #     8TourneyTier, 9TourneyLocation, 10TourneyDate, 11TourneySurface, 12TourneySurfaceInOut, 13Opponent2Countrycode,
        #     14Opponent2Name, O15pponent2ID, 16PartnerCountrycode, 17PartnerName, 18PartnerID, 19WinLoss, 20Opponent1Name, 21Opponent2Name, 22PartnerName])
        # German Format only prints wins
        if type == 'singles' and TournamentInformation[19] == result:
            #Print start of row and apply potential color coding
            ResultList.append(LocalTourneyColorFormat(TournamentInformation[7], format))
            #Print tournament win number
            ResultList.append('| ' + str(TournamentInformation[0]) + '.')
            #Print tournament date
            ResultList.append('| ' + str(LocalDateFormat(TournamentInformation[10], format)))
            #Print tournament location
            ResultList.append('| ' + str(TournamentInformation[5]))
            #Print tournament surface
            ResultList.append('| ' + str(LocalSurfaceFormat(TournamentInformation[11], TournamentInformation[12], format)))
            #Print opponent
            ResultList.append('| {{' + str(TournamentInformation[1]) + '|' + str(TournamentInformation[20]) + '|' + str(TournamentInformation[2]) + '}}')
            #Print result
            ResultList.append('| ' + str(LocalMatchResultFormat(TournamentInformation[4], format)))
            #Join list
            OutputList = ('\n'.join(ResultList))
        elif type == 'doubles' and TournamentInformation[19] == result:
            #Print start of row and apply potential color coding
            ResultList.append(LocalTourneyColorFormat(TournamentInformation[7], format))
            #Print tournament win number
            ResultList.append('| ' + str(TournamentInformation[0]) + '.')
            #Print tournament date
            ResultList.append('| ' + str(LocalDateFormat(TournamentInformation[10], format)))
            #Print tournament location
            ResultList.append('| ' + str(TournamentInformation[5]))
            #Print tournament surface
            ResultList.append('| ' + str(LocalSurfaceFormat(TournamentInformation[11], TournamentInformation[12], format)))
            # Print partner
            ResultList.append('| {{' + str(TournamentInformation[16]) + '|' + str(TournamentInformation[22]) + '|' + str(TournamentInformation[17]) + '}}')
            #Print opponents
            ResultList.append('| {{' + str(TournamentInformation[1]) + '|' + str(TournamentInformation[20]) + '|' + str(TournamentInformation[2]) + '}} <br /> {{' + str(TournamentInformation[13]) + '|' + str(TournamentInformation[21]) + '|' + str(TournamentInformation[14]) + '}}')
            #Print result
            ResultList.append('| ' + str(LocalMatchResultFormat(TournamentInformation[4], format)))
            #Join list
            OutputList = ('\n'.join(ResultList))
        return (OutputList)
    # Dutch Format prints wins and finals losses
    if format == 'nl':
        #    [0#,1Opponent1Countrycode, 2Opponent1Name, 3Opponent1ID, 4MatchResult, 5TourneyName, 6TourneyID, 7TourneyLevel,
        #     8TourneyTier, 9TourneyLocation, 10TourneyDate, 11TourneySurface, 12TourneySurfaceInOut, 13Opponent2Countrycode,
        #     14Opponent2Name, O15pponent2ID, 16PartnerCountrycode, 17PartnerName, 18PartnerID, 19WinLoss, 20Opponent1Name, 21Opponent2Name, 22PartnerName])

        # Catch exceptions which are not covered by pycountries
        exceptions = {'ANT': 'NL', 'BUL': 'BG', 'CRO': 'HR', 'CSK': 'CZ', 'GER': 'DE', 'MON': 'MC', 'NED': 'NL',
                      'POR': 'PT', 'RSA': 'ZA', 'SCG': 'RS', 'SLO': 'SI', 'SUI': 'CH', 'TPE': 'XT', '': ''}
        if TournamentInformation[1] in exceptions:
            cc1 = str(exceptions[TournamentInformation[1]])
        else:
            cc1 = str(pycountry.countries.get(alpha_3=TournamentInformation[1]).alpha_2)
        if TournamentInformation[13] in exceptions:
            cc2 = str(exceptions[TournamentInformation[13]])
        else:
            cc2 = str(pycountry.countries.get(alpha_3=TournamentInformation[13]).alpha_2)
        if TournamentInformation[16] in exceptions:
            cc3 = str(exceptions[TournamentInformation[16]])
        else:
            cc3 = str(pycountry.countries.get(alpha_3=TournamentInformation[16]).alpha_2)

        #Dutch Format  prints wins and finals losses
        if type == 'singles' and TournamentInformation[19] == result:
            #Print start of row and apply potential color coding
            ResultList.append(LocalTourneyColorFormat(TournamentInformation[7], format))
            #Print tournament win number
            ResultList.append('| ' + str(TournamentInformation[0]) + '.')
            #Print tournament date
            ResultList.append('| ' + str(LocalDateFormat(TournamentInformation[10], format)))
            #Print tournament location
            ResultList.append('| ' + str(TournamentInformation[5]))
            #Print tournament surface
            ResultList.append('| ' + str(LocalSurfaceFormat(TournamentInformation[11], TournamentInformation[12], format)))
            #Print opponent
            ResultList.append('| {{' + cc1 + '-VLAG}} [[' + str(TournamentInformation[2]) + '|' + str(TournamentInformation[2]) + ']]')
            #Print result
            ResultList.append('| ' + str(LocalMatchResultFormat(TournamentInformation[4], format)))
            ResultList.append('| ')
            #Join list
            OutputList = ('\n'.join(ResultList))
        elif type == 'doubles' and TournamentInformation[19] == result:
            #Print start of row and apply potential color coding
            ResultList.append(LocalTourneyColorFormat(TournamentInformation[7], format))
            #Print tournament win number
            ResultList.append('| ' + str(TournamentInformation[0]) + '.')
            #Print tournament date
            ResultList.append('| ' + str(LocalDateFormat(TournamentInformation[10], format)))
            #Print tournament location
            ResultList.append('| ' + str(TournamentInformation[5]))
            #Print tournament surface
            ResultList.append('| ' + str(LocalSurfaceFormat(TournamentInformation[11], TournamentInformation[12], format)))
            # Print partner
            ResultList.append('| {{' + cc3 + '-VLAG}} [[' + str(TournamentInformation[17]) + '|' + str(TournamentInformation[17]) + ']]')
            #Print opponents
            ResultList.append('| {{' + cc1 + '-VLAG}} [[' + str(TournamentInformation[2]) + '|' + str(TournamentInformation[2]) + ']] <br /> {{' + cc2 + '-VLAG}} [[' + str(TournamentInformation[14]) + '|' + str(TournamentInformation[14]) + ']]')
            #Print result
            ResultList.append('| ' + str(LocalMatchResultFormat(TournamentInformation[4], format)))
            ResultList.append('| ')
            #Join list
            OutputList = ('\n'.join(ResultList))
        return (OutputList)


    #else:
    #    return TournamentInformation

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
    soup = GetSoup(url, {})

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

        #Get details for opponent 1 (in singles and doubles)
        Opponent1Countrycode = GetCountrycode(PositionOpponent1Country.findNext('img')['src'])
        Opponent1Name = PositionOpponent1Name.contents[0].strip()
        Opponent1ID = PositionOpponent1Name['href'].split('/')[4].strip()
        PositionMatchResult = PositionOpponent1Name.findNext('a')

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
            PositionMatchResult = PositionOpponent2Name.findNext('a')
        #Get match result

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
            #Backup value in case Wikidata has no information on country code
            PartnerCountrycode = ''
            PartnerName = PositionPartner2.contents[0].strip()
            PartnerID = PositionPartner2['href'].split('/')[4].strip()

        #Return values if tournament minimum level is reached AND is not tournament is not World Team Cup
        if int(TourneyTier) >= MinimumTier and TourneyName not in excludedtourney:
            ListReturn.append([Opponent1Countrycode, Opponent1Name, Opponent1ID, MatchResult, TourneyName, TourneyID, TourneyLevel, TourneyTier, TourneyLocation, TourneyDate, TourneySurface, TourneySurfaceInOut, Opponent2Countrycode, Opponent2Name, Opponent2ID, PartnerCountrycode, PartnerName, PartnerID, Winloss, Opponent1Name, Opponent2Name, PartnerName])

    #Order tournaments in reverse to oldest to newest
    ListReturn.reverse()

    #Add number to each tournament win or finals loss
    wins = 0
    finals = 0
    for i in range(len(ListReturn)):
        if ListReturn[i][18] == 'W':
            wins = wins + 1
            number = wins
        elif ListReturn[i][18] == 'L':
            finals = finals + 1
            number = finals
        ListReturn[i].insert(0, str(number))

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

def TournamentWinsOutput(ListTournamentWins, Language, MatchType):

    #Query Wikidata for player label, link and country code
    QueryList = []
    for i in (range(len(ListTournamentWins))):
        #Select Player IDs
        PlayerID1 = ListTournamentWins[i][3].upper()
        PlayerID2 = ListTournamentWins[i][15].upper()
        PlayerID3 = ListTournamentWins[i][18].upper()

        #Only add Player IDs of not empty, e.g. for Opponent2 or Partner in case of singles
        if PlayerID1 != '':
            QueryList.append(PlayerID1)
        if PlayerID2 != '':
            QueryList.append(PlayerID2)
        if PlayerID3 != '':
            QueryList.append(PlayerID3)

    #Format list to string
    InputIDs = '\"' + '\"\n\"'.join(QueryList) + '\"'

    #Derive Player information from Wikidata by Player-ID
    WikidataPlayerInfo = WikidataGetPlayerInfoshort('atp', InputIDs, Language)
    for j in range(len(ListTournamentWins)):
        for k in range(len(WikidataPlayerInfo)):
            if ListTournamentWins[j][3].upper() == WikidataPlayerInfo[k][1]:
                ListTournamentWins[j][1] = WikidataPlayerInfo[k][4]
                ListTournamentWins[j][2] = WikidataPlayerInfo[k][2]
                ListTournamentWins[j][20] = WikidataPlayerInfo[k][3]
            if ListTournamentWins[j][15].upper() == WikidataPlayerInfo[k][1]:
                ListTournamentWins[j][13] = WikidataPlayerInfo[k][4]
                ListTournamentWins[j][14] = WikidataPlayerInfo[k][2]
                ListTournamentWins[j][21] = WikidataPlayerInfo[k][3]
            if ListTournamentWins[j][18].upper() == WikidataPlayerInfo[k][1]:
                ListTournamentWins[j][16] = WikidataPlayerInfo[k][4]
                ListTournamentWins[j][17] = WikidataPlayerInfo[k][2]
                ListTournamentWins[j][22] = WikidataPlayerInfo[k][3]

    # Build the respective countries result format
    # Build format for de.wp
    if Language == 'de':
        # Write Header for tournament wins
        OutputHeader = LocalTableFormat(Language, MatchType)
        # Write tournament wins
        OutputPlayer = []
        for i in range(len(ListTournamentWins)):
            #only add lines if they contain tournament results, i.e. avoid empty results which get appended by a newline
            if LocalTourneyFormat(ListTournamentWins[i], Language, MatchType, 'W') != '':
                OutputPlayer.append(LocalTourneyFormat(ListTournamentWins[i], Language, MatchType, 'W'))
        OutputList = ('\n'.join(OutputPlayer))
        OutputClose = '\n|}'
        Output = OutputHeader + OutputList + OutputClose
    if Language == 'nl':
        # Write Header for tournament wins
        OutputHeader1 = LocalTableFormat(Language, MatchType)
        # Write tournament wins
        OutputPlayer = []
        for i in range(len(ListTournamentWins)):
            #only add lines if they contain tournament results, i.e. avoid empty results which get appended by a newline
            if LocalTourneyFormat(ListTournamentWins[i], Language, MatchType, 'W') != '':
                OutputPlayer.append(LocalTourneyFormat(ListTournamentWins[i], Language, MatchType, 'W'))
        OutputList1 = ('\n'.join(OutputPlayer))
        # Write final losses
        if MatchType == 'singles':
            OutputHeader2 = '\n|- bgcolor=\"#efefef\" align=\"center\"\n|colspan=\"8\"| \'\'\'Verloren finales \'\'\'\n'
        elif MatchType == 'doubles':
            OutputHeader2 = '\n|- bgcolor=\"#efefef\" align=\"center\"\n|colspan=\"8\"| \'\'\'Verloren finales herendubbel\'\'\'\n'
        OutputPlayer2 = []
        for i in range(len(ListTournamentWins)):
            #only add lines if they contain tournament results, i.e. avoid empty results which get appended by a newline
            if LocalTourneyFormat(ListTournamentWins[i], Language, MatchType, 'L') != '':
                    OutputPlayer2.append(LocalTourneyFormat(ListTournamentWins[i], Language, MatchType, 'L'))
        OutputList2 = ('\n'.join(OutputPlayer2))
        #Close table and consolidate complete output
        OutputClose = '\n|}'
        Output = OutputHeader1 + OutputList1 + OutputHeader2 + OutputList2 + OutputClose

    return Output
