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

    query = """SELECT DISTINCT ?player ?playerLabel ?PlayerID ?Wikipedia ?Wikipedia_language_code ?sitelink ?country_code
                ?ar_sitelink ?de_sitelink ?en_sitelink ?es_sitelink ?fa_sitelink ?fr_sitelink ?it_sitelink ?ja_sitelink ?nl_sitelink ?pl_sitelink ?pt_sitelink ?ru_sitelink 
WHERE {
  VALUES ?PlayerID { %s }
  VALUES ?language_code { "%s" }

  # Find the player
  ?player wdt:P536 ?PlayerID.

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
  ?player wdt:P27 ?citizenship.
  BIND (COALESCE(?represents, ?citizenship) AS ?country)
  ?country wdt:P298 ?country_code.

  # Sitelinks to selected Wikipedias
   OPTIONAL {
    ?ar_sitelink schema:about ?player.
    ?ar_sitelink schema:isPartOf <https://ar.wikipedia.org/>.
  }
   OPTIONAL {
    ?de_sitelink schema:about ?player.
    ?de_sitelink schema:isPartOf <https://de.wikipedia.org/>.
  }
  OPTIONAL {
    ?en_sitelink schema:about ?player.
    ?en_sitelink schema:isPartOf <https://en.wikipedia.org/>.
  }
  OPTIONAL {
    ?es_sitelink schema:about ?player.
    ?es_sitelink schema:isPartOf <https://es.wikipedia.org/>.
  }
  OPTIONAL {
    ?fa_sitelink schema:about ?player.
    ?fa_sitelink schema:isPartOf <https://fa.wikipedia.org/>.
  }  
  OPTIONAL {
    ?fr_sitelink schema:about ?player.
    ?fr_sitelink schema:isPartOf <https://fr.wikipedia.org/>.
  }  
  OPTIONAL {
    ?it_sitelink schema:about ?player.
    ?it_sitelink schema:isPartOf <https://it.wikipedia.org/>.
  }
  OPTIONAL {
    ?ja_sitelink schema:about ?player.
    ?ja_sitelink schema:isPartOf <https://ja.wikipedia.org/>.
  }
  OPTIONAL {
    ?nl_sitelink schema:about ?player.
    ?nl_sitelink schema:isPartOf <https://nl.wikipedia.org/>.
  }  
  OPTIONAL {
    ?pl_sitelink schema:about ?player.
    ?pl_sitelink schema:isPartOf <https://pl.wikipedia.org/>.
  }   
  OPTIONAL {
    ?pt_sitelink schema:about ?player.
    ?pt_sitelink schema:isPartOf <https://pt.wikipedia.org/>.
  }     
  OPTIONAL {
    ?ru_sitelink schema:about ?player.
    ?ru_sitelink schema:isPartOf <https://ru.wikipedia.org/>.
  }
}""" % (PlayerID, LanguageFormat)

    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    dic = results["results"]["bindings"]

    # Split Player ID string to a list in order of the world ranks
    PlayerIDList = list(PlayerID.replace('"', '').replace('\n', ' ').split(' '))
    # Initiate Return List outside the loop
    ReturnList = []
    for i in range(len(dic)):
        # Initiate Player Info List inside the loop
        PlayerInfo = []
        # Get Wikidata Q-ID
        WDID = dic[i]['player']['value'].split('entity/')[1]
        PlayerInfo.append(WDID)
        # Player ATP-ID
        PlayerID = dic[i]['PlayerID']['value']
        PlayerInfo.append(PlayerID)
        # Ranking #
        PlayerRank = int(PlayerIDList.index(PlayerID)) + 1
        PlayerInfo.append(PlayerRank)
        # Get Player Label in local format
        PlayerLabel = dic[i]['playerLabel']['value']
        PlayerInfo.append(PlayerLabel)
        # Get article lemma in local format
        WPLemma = urllib.parse.unquote(dic[i]['sitelink']['value'].split('wiki/')[1])
        PlayerInfo.append(WPLemma)
        # Player Countrycode
        PlayerCountry = dic[i]['country_code']['value']
        PlayerInfo.append(PlayerCountry)
        # Get the keys from the SPARQL query as a list
        keys = list(dic[i].keys())
        Templist = []
        for n in range(len(keys)):
            Sitelinks = []
            if "sitelink" in keys[n]:
                # Get the values in case the key contains "sitelink"
                values = list(dic[i].values())[n]['value']
                # Get language code as the first two characters after https://
                WPLang = str(values).split('https://')[1][:2]
                Sitelinks.append(WPLang)
                # Get local wiki link
                WPLink = urllib.parse.unquote(str(values).split('wiki/')[1])
                Sitelinks.append((WPLink))
            # Include only sitelinks that are not empty and don't link to the home wiki
            if len(Sitelinks) > 0 and WPLang != LanguageFormat:
                Templist.append(Sitelinks)
        PlayerInfo.append(Templist)

        # Add Player Info to Return List of list
        ReturnList.append(PlayerInfo)
    # Sort Results by World Ranking Position
    ReturnList.sort(key=lambda x: x[2])
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