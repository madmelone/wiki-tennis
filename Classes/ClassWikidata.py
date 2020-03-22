# Name:     ClassWikidata
# Author:   Michael Frey
# Version:  0.1
# Date:     20-03-2020
# Content:  Provide functions to interact with Wikidata

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