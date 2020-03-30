# Name:     ClassWikidata
# Author:   Michael Frey
# Version:  0.2
# Date:     29-03-2020
# Content:  Provide functions to interact with Wikidata

#List of imports
from Settings import countryformat

def GetWTAID(wd):
    #Returns WTA-ID by Wikidata-ID
    from wikidata.client import Client
    client = Client()
    entity = client.get(wd, load=True)
    #get WTA-ID
    wtaid = entity[client.get('P597')]
    return(wtaid)

def GetITFID(wd):
    # Returns ITF-ID by Wikidata-ID
    from wikidata.client import Client
    client = Client()
    entity = client.get(wd, load=True)
    #get ITF-ID
    itfid = entity[client.get('P599')]
    return(itfid)

def GetATPID(wd):
    #Returns ATP-ID by Wikidata-ID
    from wikidata.client import Client
    client = Client()
    entity = client.get(wd, load=True)
    #get WTA-ID
    wtaid = entity[client.get('P536')]
    return(atpid)


def WikidataGetPlayerInfo(RankingOrg, PlayerID, LanguageFormat):
    from SPARQLWrapper import SPARQLWrapper, JSON
    import urllib.parse
    endpoint_url = "https://query.wikidata.org/sparql"

    query = """SELECT DISTINCT ?player ?playerLabel ?Wikipedia ?Wikipedia_language_code ?sitelink ?country_code             
            WHERE {
              VALUES ?Player_ID { "%s" }
              VALUES ?language_code { "%s" }

              # Find the player
              ?player wdt:P536 ?Player_ID.

              # Find the Wikipedia, its language(s), and sitelink for the Wikipedia
              BIND (URI(CONCAT("https://", ?language_code, ".wikipedia.org/")) AS ?Wikipedia)
              ?sitelink schema:about ?player.
              ?sitelink schema:isPartOf ?Wikipedia.
              ?Wikipedia ^wdt:P856/wdt:P407/wdt:P424 ?Wikipedia_language_code. hint:Prior hint:gearing "forward".

              # Find player's label in the language(s)
              ?player rdfs:label ?playerLabel.
              FILTER (LANG(?playerLabel) = ?Wikipedia_language_code)

              # Find the country/ies and country code(s)
              OPTIONAL { ?player wdt:P1532 ?represents. }
              OPTIONAL { ?player wdt:P27 ?citizenship. }
              BIND (COALESCE(?represents, ?citizenship) AS ?country)
              ?country wdt:P298 ?country_code.
            }""" % (PlayerID, LanguageFormat)

    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    dic = results["results"]["bindings"][0]
    ReturnList = []
    # Get Wikidata Link
    WDLink = dic['player']['value']
    ReturnList.append(WDLink)
    # Get Wikidata Q-ID
    WDID = dic['player']['value'].split('entity/')[1]
    ReturnList.append(WDID)
    # Get Player Label in local format
    PlayerLabel = dic['playerLabel']['value']
    ReturnList.append(PlayerLabel)
    # Get article lemma in local format
    WPLemma = urllib.parse.unquote(dic['sitelink']['value'].split('wiki/')[1])
    ReturnList.append(WPLemma)
    # Player Countrycode
    PlayerCountry = dic['country_code']['value']
    ReturnList.append(PlayerCountry)
    return ReturnList

def WikidataGetPlayerLinks(PlayerID, LanguageFormat = countryformat):
    from SPARQLWrapper import SPARQLWrapper, JSON
    import urllib.parse
    endpoint_url = "https://query.wikidata.org/sparql"

    query = """SELECT DISTINCT ?playerLabel ?Wikipedia_language_code ?sitelink             
            WHERE {
              VALUES ?Player_ID { "%s" }

              # Find the player
              ?player wdt:P536 ?Player_ID.

              # Find the Wikipedia, its language(s), and sitelink for the Wikipedia
              ?sitelink schema:about ?player.
              ?sitelink schema:isPartOf ?Wikipedia.
              ?Wikipedia ^wdt:P856/wdt:P407/wdt:P424 ?Wikipedia_language_code. hint:Prior hint:gearing "forward".

              # Find player's label in the language(s)
              ?player rdfs:label ?playerLabel.
              FILTER (LANG(?playerLabel) = ?Wikipedia_language_code)
              FILTER ( ?Wikipedia_language_code != "%s" ) 
            }""" % (PlayerID, LanguageFormat)

    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    sitelinks = results['results']['bindings']

    ReturnList = []
    for i in range(len(sitelinks)):
        LinkList = []
        dic = sitelinks[i]
        # Get Wikipedia language code
        WPCode = dic['Wikipedia_language_code']['value']
        LinkList.append(WPCode)
        # Get local lemma
        WPLemma = urllib.parse.unquote(dic['sitelink']['value'].split('wiki/')[1])
        LinkList.append(WPLemma)
        # Get Player Label
        PlayerLabel = dic['playerLabel']['value']
        LinkList.append(PlayerLabel)
        ReturnList.append(LinkList)
    return ReturnList
