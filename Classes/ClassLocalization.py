# Name:     ClassWikidata
# Author:   Michael Frey
# Version:  0.1
# Date:     20-03-2020
# Content:  Provide functions to interact with Wikidata

#Internal imports
from Settings import countryformat

#External imports
from datetime import datetime
import locale

def LocalDateFormat(datestring, format=countryformat):
    #Returns date in defined local format
    date = datetime.strptime(datestring, '%Y-%m-%d')
    if format == 'de':
        locale.setlocale(locale.LC_TIME, "de_DE")
        #Delete leading zero in day of the month
        day = date.strftime('%d. ').replace('0', '')
        #Concatenate day and rest of the date
        return day + date.strftime('%B %Y')
    else:
        return date.strftime('%Y-%m-%d')

def LocalSurfaceFormat(Surface, InOut='O', format=countryformat):
    #Returns surface in translated local format
    if format == 'de':
        #Translate to local values
        SurfaceTranslation = {'Hard':'Hartplatz', 'Clay':'Sandplatz', 'Grass':'Rasen', 'Carpet':'Teppich'}
        InOutTranslation = {'I':'Halle', 'O':''}
        #Apply local format
        if InOut == 'I':
            return SurfaceTranslation[Surface] + ' (' + InOutTranslation[InOut] + ')'
        else:
            return SurfaceTranslation[Surface]
    else:
        return Surface

def LocalMatchResultFormat(result, format=countryformat):
    #Returns match result in defined local format
    #Change result to string format if list (in case of tiebreaks)
    if len(result) > 1:
        templist = []
        for i in range(len(result)):
            templist.append(str(result[i]))
        result = (''.join(templist))

    setlist = []
    #Split the individual sets from the result input
    sets = str(result).strip(',[]\',').split()
    # Apply chosen format per sets
    if format == 'de':
        for i in range(len(sets)):
            if sets[i] == '(RET)':
                set = 'Aufgabe'
            else:
                set = str(sets[i][0]) + ':' + str(sets[i][1:])
            setlist.append(set)
        return (', '.join(setlist))
    else:
        return result

def LocalTourneyColorFormat(TourneyTier):
    TourneyColor = {'challenger': '#EEEEEE;', '1000s': '#DFE2E9;', '500':'#D1EEEE', 'grandslam': '#E5D1CB;', 'olmypics': '#FFD700;', 'tourfinals': 'FFFFCC;'}
    if TourneyTier not in TourneyColor:
        return '|-'
    else:
        return '|- style = "background:' + str(TourneyColor[TourneyTier]) + '"'