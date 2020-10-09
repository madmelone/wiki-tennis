# Name:     ITF Tournament scraper
# Author:   Somnifuguist (w.wiki/fDy)
# Date:     10-10-2020
# Content:  Scrapes data from ITF printable draws

import itertools
import re

from ClassSupportFunctions import GetSoup

def ExtractTeam(team):
    # Extracts [name, country code, [seeds]] for player(s) in team from string.
    team = team.text.strip(" \n").replace("\xa0", " ")
    players = team.split(" / ")
    team_data = []
    for player in players:
        if player == "":
            team_data.append(["","",[]])
        elif player == "BYE":
            team_data.append(["BYE", "", []])
        else:
            country = re.search(r"\([A-Z]{3}\)", player).group()[1:4]
            seed = []
            digit = re.search(r"\[\d{1,2}\]", player)
            if digit:
                seed.append(digit.group()[1:-1])
            types = ["LL", "WC", "Q", "PR", "Alt", "SR", "A"]
            for t in types:
                if re.search(r"\(" + t + "\)", player):
                    seed.append(t)
            name = (player.replace("(" + country + ")", "").replace("(" + (seed[-1] if seed != [] else "") + ")", "").replace("[" + (seed[0] if seed != [] else "")  + "]", "").strip(" ").replace(",", ""))
            team_data.append([name, country, seed])
    return team_data

def ExtractScore(score, match, winners):
    # Extracts [[winner, [set winners]], [set 1 scores], [set 2 scores], ...] from string
    # Set scores = [player 0 score, player 1 score, [tiebreak scores if tiebreak]/"Retired" if retirement]
    # Player and scores ordered by order in draw.
    # e.g. the score 6-4 5-7 7-6(5) 6-0, with player 1 as winner = [[1, [1, 0, 1, 1]], [4, 6], [7, 5], [6, 7, [5, 7]], [0, 6]]
    # Walkovers = [[winner, ["w/o"]], ["Walkover"]]
    # Byes = [[winner, []], ["BYE"]]
    winner = 0 if match[0][0][0] in winners and match[0][0][0] != "BYE" else 1
    score = score.text.strip(" |\n")
    score = [s.split("-") for s in score.split(" ")]

    if match[0][0][0] == "BYE" or match[1][0][0] == "BYE":
        new_score = [[winner, []], ["BYE"]]
    elif score[0][0] == "Walkover":
        new_score = [[winner, ["w/o"]], ["Walkover"]]
    else:
        new_score = [[winner, []]]
        for set in score:
            set = [f.replace("[", "").replace("]", "") for f in set]
            if set == ["Retired"]:
                if max(int(new_score[-1][0]), int(new_score[-1][1])) > 5 and abs(int(new_score[-1][0]) - int(new_score[-1][1])) > 1:
                    new_score.append(['0', '0', "Retired"]) # retirement happened after set finished
                else:
                    new_score[-1] += set # retirement happened mid-set
            elif set != [""]:
                tiebreaker = re.search(r"\(\d{1,}\)", set[1])
                if tiebreaker:
                    tie_l = int(tiebreaker.group()[1:-1])
                    tie_w = tie_l + 2 if tie_l > 4 else 7
                    if set[0] == '7':
                        set = ['7', '6', [str(tie_w), str(tie_l)]]
                    else:
                        set = ['6', '7', [str(tie_l), str(tie_w)]]
                new_score.append(set)

        if winner == 1: # reverse score order, as scores are always ordered with winner first
            for c, f in enumerate(new_score[1:]):
                if "Retired" in f:
                    new_score[c+1] = f[:-1][::-1] + [f[-1]]
                elif len(f) == 3 and len(f[2]) == 2: # tiebreak
                    new_score[c+1] = f[:-1][::-1] + [f[-1][::-1]]
                else:
                    f.reverse()
        for set in new_score[1:]: # fill new_score[0][1] with winner of each set, "r" if team retires
            if 'Retired' in set:
                new_score[0][1].append("r")
            else:
                new_score[0][1].append(int(int(set[0])<int(set[1])))
    return new_score

def ExtractTournament(soup, qual, doubles):
    round_names = [f.text.strip(" \n") for f in soup.find_all("div", {"id": "divRound"})]
    rounds = soup.find_all("li", {"id": "liRound"}) # contains all matches in each round

    if qual:
        winners = [ExtractTeam(f.span)[0][0] for f in soup.find_all("li", {"id": "liQWinners"})]
        scores = [f.find("div", {"style": "padding: 2px 3px 0px 3px; height: 18px;"}) for f in soup.find_all("li", {"id": "liQWinners"})]
    else:
        winners = [ExtractTeam(f)[0][0] for f in soup.find_all("div", {"id": "divWinner"})]
        scores = soup.find_all("div", {"style": "padding: 2px 3px 0px 3px;"})

    matches = []

    # Move backwards through draw as each round contains winner and score of previous round
    for r in rounds[::-1]:
        top = [ExtractTeam(f) for f in r.find_all("span", {"id": ["spnPlayerTop1", "spnPlayerTop1Bye"]})]
        bottom = [ExtractTeam(f) for f in r.find_all("span", {"id": ["spnPlayerBottom1", "spnPlayerBottom1Bye"]})]

        # Zip doubles teams together
        if doubles:
            top_2 = [ExtractTeam(f)[0] for f in r.find_all("span", {"id": ["spnPlayerTop2", "spnPlayerTop2Bye"]})]
            bottom_2 = [ExtractTeam(f)[0] for f in r.find_all("span", {"id": ["spnPlayerBottom2", "spnPlayerBottom2Bye"]})]
            top = [x for x in itertools.chain.from_iterable(itertools.zip_longest([f[0] for f in top], top_2))]
            bottom = [x for x in itertools.chain.from_iterable(itertools.zip_longest([f[0] for f in bottom], bottom_2))]
            top = list(top[i:i+2] for i in range(0, len(top), 2))
            bottom = list(bottom[i:i+2] for i in range(0, len(bottom), 2))

        matches = [list([list(f) for f in tuple(zip(top, bottom))])] + matches # zip players into match

        for c, m in enumerate(matches[0]):
            score = ExtractScore(scores[c], m, winners)
            matches[0][c].append(score)

        winners = [f[0][0] for f in top + bottom] # teams in round n are winners of round n-1 (next loop)
        # Scores for matches in previous round (next loop)
        top_scores = r.find_all("div", {"style": "border-right: 1px solid #999; padding: 2px 3px 0px 3px; line-height: 12px;"})
        bottom_scores = r.find_all("div", {"style": "padding: 2px 3px 0px 3px; height: 18px;"})
        scores = [x for x in itertools.chain.from_iterable(itertools.zip_longest(top_scores,bottom_scores))]
    return matches

def FixByes(soup):
    # Fixes error in draw html where player name in bracket is '' instead of 'BYE'
    empty = ['<div class="hlPlayer" id="divPlayerTop" style="border-bottom: 1px solid #999; padding: 0px 3px 2px 3px;"><span style="display: block; height: 12px;"></span></div>',
    '<div class="hlPlayer" id="divPlayerBottom" style="border-bottom: 1px solid #999; border-right: 1px solid #999; padding: 0px 3px 2px 3px;"><span style="display: block; height: 12px;"></span></div>',
    '<div class="hlPlayer" id="divPlayerTop" style="border-bottom: 1px solid #999; padding: 0px 3px 2px 3px;"><span style="display: block; height: 11px;"></span></div>',
    '<div class="hlPlayer" id="divPlayerBottom" style="border-bottom: 1px solid #999; border-right: 1px solid #999; padding: 0px 3px 2px 3px;"><span style="display: block; height: 11px;"></span></div>']
    bye = ['<div class="hlPlayer" id="divPlayerTop" style="border-bottom: 1px solid #999; padding: 0px 3px 2px 3px;"><span style="display: block; height: 12px;"><span id="spnPlayerTop1">BYE</span></span></div>',
    '<div class="hlPlayer" id="divPlayerBottom" style="border-bottom: 1px solid #999; border-right: 1px solid #999; padding: 0px 3px 2px 3px;"><span style="display: block; height: 12px;"><span id="spnPlayerBottom1">BYE</span></span></div>',
    '<div class="hlPlayer" id="divPlayerTop" style="border-bottom: 1px solid #999; padding: 0px 3px 2px 3px;"><span style="display: block; height: 11px;"><span id="spnPlayerTop1">BYE</span></span></div>',
    '<div class="hlPlayer" id="divPlayerBottom" style="border-bottom: 1px solid #999; border-right: 1px solid #999; padding: 0px 3px 2px 3px;"><span style="display: block; height: 11px;"><span id="spnPlayerBottom1">BYE</span></span></div>']
    html = ">".join([f.strip("\t\n ") for f in str(soup).split(">")])
    for i in range(4):
        html = html.replace(empty[i], bye[i])
    soup = GetSoup(html, True)
    return soup

def ScrapeTournamentITF(url, qual, doubles):
    soup = GetSoup(url, {})
    try:
        data = ExtractTournament(soup, qual=qual, doubles=doubles)
    except IndexError: # html is missing name in tournament bracket
        soup = FixByes(soup)
        data = ExtractTournament(soup, qual=qual, doubles=doubles)
    return data
