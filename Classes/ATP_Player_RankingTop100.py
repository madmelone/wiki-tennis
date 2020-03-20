# Name:     ATP Player RankingTop100
# Author:   Michael Frey
# Version:  0.1
# Date:     20-03-2020
# Content:  Returns the current Top 100 ATP World Rankings

import requests
from bs4 import BeautifulSoup

def GetPlayerRankingTop100(org = "atp", competition="singles"):

    #Set URL
    if competition == "singles":
        url = "https://www.atptour.com/en/rankings/singles"
        filename = "top100_singles.csv"
    elif competition == "doubles":
        url = "https://www.atptour.com/en/rankings/doubles"
        filename = "top100_doubles.csv"
    else:
        print("Fehlerhafter Parameter")
        exit()

    #open ATP ranking website
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")

    #read rank and player information from website
    ranks = soup.findAll("td", { "class" : "rank-cell" })
    players = soup.findAll("td", { "class" : "player-cell" })

    #write information into file
    #f = open(filename, "w")
    for i in range(len(ranks)):
        rank = str(ranks[i].get_text()).strip()
        player = str(players[i].get_text()).strip()
       # f.write(rank + ";" + player +"\n")
    #f.close()

    #write information into csv
    import csv
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Rank", "Name"])
        for i in range(len(ranks)):
            rank = str(ranks[i].get_text()).strip()
            player = str(players[i].get_text()).strip()
            writer.writerow([rank, player])

GetPlayerRankingTop100()