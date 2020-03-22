
from Settings import countryformat
from datetime import datetime
import locale


def LocalDateFormat(datestring, format=countryformat):
    date = datetime.strptime(datestring, '%Y-%m-%d')
    if format == 'de':
        locale.setlocale(locale.LC_TIME, "de_DE")
        return date.strftime('%d. %B %Y')
    else:
        return date.strftime('%Y-%m-%d')

def LocalSurfaceFormat(string, format=countryformat):
    #Local translations of the English surface names
    if format == 'de':
        translation = {'Hard':'Hartplatz', 'Clay':'Sandplatz', 'Grass':'Rasen', 'Carpet':'Teppich'}
        return translation[string]
    else:
        return string

def LocalMatchResultFormat(result, format=countryformat):
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
        return string