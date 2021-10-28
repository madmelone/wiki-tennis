import copy
import datetime
import hashlib
import math
import re
import sys
import time

from ClassSupportFunctions import *

flags = LoadJSON("data/FlagsATP.json")

errors = ""
format = None

def ExtractScore(score):
    global errors
    global format

    ties = [f.text.strip() for f in score.find_all("sup")]
    for s in score('sup'):
        s.decompose()
    score = [f.strip() for f in score.text.strip().split("\n")if f.strip() != '']

    if score == ["(W/O)"]:
        new_score = [[0, ["w/o"]], ["Walkover"]]
    else:
        new_score = [[0, []]]
        tie_index = 0
        for s in score:
            if s == "(RET)":
                if len(new_score) == 1:
                    new_score.append(['0', '0', "Retired"]) # retirement happened before first game of match finished
                else:
                    if (max(int(new_score[-1][0]), int(new_score[-1][1])) > 5 and abs(int(new_score[-1][0]) - int(new_score[-1][1])) > 1):
                        new_score.append(['0', '0', "Retired"]) # retirement happened after set finished
                    elif (len(new_score[-1]) == 3 and abs(int(new_score[-1][-1][0]) - int(new_score[-1][-1][1])) > 1) or (int(new_score[-1][0]) + int(new_score[-1][1]) == 13):
                        new_score.append(['0', '0', "Retired"]) # retirement happened after tiebreak set finished
                    elif len(new_score[-1]) == 2:
                        new_score[-1] += ['Retired'] # retirement happened mid-set
            elif s == "(DEF)":
                if len(new_score) == 1:
                    new_score.append(['0', '0', "Default"]) # default happened before first game of match finished
                else:
                    if (max(int(new_score[-1][0]), int(new_score[-1][1])) > 5 and abs(int(new_score[-1][0]) - int(new_score[-1][1])) > 1):
                        new_score.append(['0', '0', "Default"]) # default happened after set finished
                    elif (len(new_score[-1]) == 3 and abs(int(new_score[-1][-1][0]) - int(new_score[-1][-1][1])) > 1) or (int(new_score[-1][0]) + int(new_score[-1][1]) == 13):
                        new_score.append(['0', '0', "Default"]) # default happened after tiebreak set finished
                    elif len(new_score[-1]) == 2:
                        new_score[-1] += ['Default'] # default happened mid-set
            elif s == "(W/O)":
                pass
            else:
                new_set = []
                if "-" in s:
                    format = 2
                    new_set = s.split("-")
                elif len(s) == 2:
                    new_set = [s[0], s[1]]
                elif len(s) == 1:
                    if "Partial" not in errors:
                        errors += "</br>WARNING: partial score in draw; check every score for errors."
                    continue
                elif len(s) ==4:
                    new_set = [s[:2], s[2:]]
                else:
                    if int(s[0]) == int(s[1:]) - 2:
                        new_set = [s[0], s[1:]]
                    else:
                        new_set = [s[:2], s[2:]]
                if int(new_set[0]) + int(new_set[1]) == 13 and ties != []:
                    tie_l = int(ties[0])
                    tie_w = tie_l + 2 if tie_l > 4 else 7
                    if new_set[0] == '7':
                        new_set = ['7', '6', [str(tie_w), str(tie_l)]]
                    else:
                        new_set = ['6', '7', [str(tie_l), str(tie_w)]]
                    del ties[0]
                new_score.append(new_set)

        for set in new_score[1:]:
            if 'Retired' in set:
                new_score[0][1].append("r")
            elif 'Default' in set:
                new_score[0][1].append("d")
            else:
                new_score[0][1].append(int(int(set[0])<int(set[1])))
    return new_score

def get_sequence(rounds):
    # the key insight needed to scrape these draws.
    # round of each match by index in scores list, derived from https://oeis.org/A082850
    # required to reorder the results from left-righ top to bottom to the match order
    s = []
    for i in range(1,rounds + 2):
        s = s + s + [i]
    sequence = s[s.index(rounds)-rounds+1:s.index(rounds)-rounds+2**rounds]
    return sequence

def Reorder(players, winners, scores, qual):
    # Reorder scores that the first instance of each player is their first match
    if not qual:
        rounds = int(math.log2(len(players)))
        sequence = get_sequence(rounds)
    else:
        qual_rounds = 0
        match_count = len(winners)
        while match_count > 0:
            match_count -= len(players) * ((1/2) ** (qual_rounds + 1))
            qual_rounds += 1
        rounds = math.ceil(math.log2(len(players)))
        sequence = [f for f in get_sequence(rounds) if f <= qual_rounds]

    for c, player in enumerate(players):
        match_indices = [i for i, x in enumerate(winners) if x == player]
        matches_won = len(match_indices)

        match_indices_rounds = [[match_indices[p], sequence[match_indices[p]]] for p in range(matches_won)] # round no. of each match in indices
        reordered_matches = [f[0] for f in sorted(match_indices_rounds, key=lambda x: x[1])] # sort matches into chronological order

        scores_copy = copy.deepcopy(scores)
        for i in range(matches_won):
            scores[match_indices[i]] = scores_copy[reordered_matches[i]]

    scores_indices_rounds = [[sequence[p], scores[p]] for p in range(len(scores))] # round no. of each match in indices
    reordered_scores = [f[1] for f in sorted(scores_indices_rounds, key=lambda x: x[0])] # sort matches into chronological order
    return scores

def ReverseScore(score):
    if score == "(NA)":
        return score
    else:
        for c, f in enumerate(score[1:]):
            if "Retired" in f or "Default" in f:
                score[c+1] = f[:-1][::-1] + [f[-1]]
            elif len(f) == 3 and len(f[2]) == 2: # tiebreak
                score[c+1] = f[:-1][::-1] + [f[-1][::-1]]
            else:
                f.reverse()
        score[0][0] = 1
        set_winners = []
        for set in score[0][1]:
            if set == "w/o":
                set_winners.append("w/o")
            elif set == "d" or set == "r":
                set_winners.append(1)
            else:
                set_winners.append(int(not set))
        score[0][1] = set_winners
    return score

def FillMatches(matches, winners, scores):
    max_winners_left = 0
    while len(winners) > max_winners_left:
        matches += [[]]
        new_match = []
        for c, match in enumerate(matches[-2]):
            error = False
            winner = not match[0][0][0] in winners
            new_match.append(match[winner])

            try:
                index = winners.index(match[winner][0][0]) # Scores must be in order so that the first instance of each player is their first match, hence Reorder()
            except ValueError:
                global errors
                if winners.count(None) > 0:
                    if "2nd round" not in errors:
                        errors += "</br>WARNING: match data missing in 2nd round or later; check every match for errors."
                    index = winners.index(None)
                else:
                    if "issues" not in errors:
                        errors += "</br>WARNING: match data has issues; check every match for errors."
                    max_winners_left += 1
                    error = True
                    matches[-2][c].append([[0, []], ["BYE"]])

            if not error:
                matches[-2][c].append(ReverseScore(scores[index]) if winner else scores[index])
                del winners[index]
                del scores[index]

            if c%2 == 1:
                matches[-1].append(new_match)
                new_match = []
    return matches[:-1]

def ExtractTeam(team, doubles):
    qual = re.search("QUALIFIER\d*\n", team.text)
    if qual != None and not doubles:
        return [[qual.group()[:-1], "", ["Q"]]]
    players = team.find_all('a', {'class': 'scores-draw-entry-box-players-item'})
    team_data = []
    if players != []:
        for p in players:
            player = p['data-ga-label']
            seed = [""]
            if team.find('span') != None:
                aliases = {"AL":"Alt", "S":"SE"}
                seed = [f.strip("()") for f in team.find('span').text.strip().split(" ")]
                allowed = ["AL", "Alt", "ITF", "JE", "LL", "PR", "Q", "S", "SE", "WC"]
                for c, s in enumerate(seed):
                    if not s.isdigit():
                        if s in aliases:
                            seed[c] = aliases[s]

            flag_b64 = p.find('img', {'class': 'scores-draw-entry-box-players-item-flag'})['src'][26:]
            flag_hash = hashlib.md5(flag_b64.encode('utf-8')).hexdigest()
            country = ""

            if flag_hash not in flags:
                player_id = re.search("\w{4}\/overview", team.a['href']).group()[:4].upper()
                url = "https://www.atptour.com/-/ajax/Head2HeadSearch/GetHead2HeadData/F324/" + player_id
                country = GetSoup(url, 'json')['playerRight']['PlayerCountryCode']
                flags[flag_hash] = country
                SaveJSON("data/FlagsATP.json", flags)
                time.sleep(5)
            else:
                country = flags[flag_hash]

            team_data.append([player, country, seed])
    elif "bye" in team.text.strip().lower():
        team_data = [["BYE", "", [""]]] * (2 if doubles else 1)
    else:
        team_data = [["PLAYER MISSING", "", [""]]] * (2 if doubles and qual == None else 1)
    if qual != None:
        team_data.append([qual.group()[:-1], "", ["Q"]])
    return team_data

def AddMissingRounds(data, doubles):
    base = [[['', '', ["BYE"]]* (2 if doubles else 1)]] * 2 + [[[0, []], ["BYE"]]] # blank match
    data = [f for f in data if f != []]
    rounds = int(math.log(len(data[-1]), 2)) # missing rounds to add
    while rounds > 0:
        data.append([base] * (2 ** (rounds - 1)))
        rounds -= 1
    return data

def ExtractTournament(soup, qualifying, doubles):
    global errors

    table = soup.find_all('div', {'class': 'scores-draw-entry-box'})
    matches = [[]]
    players = []
    matches_corrected = [[]]

    match_corrected = []
    for t in table:
        trs = t.find_all('tr')
        match = []
        for c, tr in enumerate(trs):
            m = ExtractTeam(tr, doubles)
            match.append(m)
            if ["PLAYER MISSING", "", [""]] not in m:
                match_corrected.append(m)

            players.append(m[0][0])
            if len(match_corrected) == 2:
                matches_corrected[0].append(match_corrected.copy())
                match_corrected = []

        if len(match) == 1:
            match.append([["PLAYER MISSING", "", [""]]] * (2 if doubles else 1))
            players.append("PLAYER MISSING")
            if "Player data missing" not in errors:
                errors += "</br>WARNING: player data missing; check every match for errors."
        if match != []:
            matches[0].append(match)

    winners = []
    scores = []
    byes = []
    for t in table:
        score = t.find('a', {'class':'scores-draw-entry-box-score'})
        if score != None:
            if any(f in score.text.strip() for f in ["(NA)", "(UNP)", "(WEA)", "(ABN)"]):
                winner = None
                score = [[0, []], ["BYE"]]
                if "NA/UNP/WEA/ABN" not in errors:
                    errors += "</br>WARNING: NA/UNP/WEA/ABN matches; Check every match for errors."

            else:
                boxes = t.find('div', {'class': 'scores-draw-entry-box'})
                all_players = t.find_all('a', {'class': 'scores-draw-entry-box-players-item'})
                qual = ""
                try:
                    winner = all_players[0]['data-ga-label']
                except:
                    try:
                        winner = re.search("QUALIFIER\d+Q", str(t)).group()[:-1]
                    except:
                        try:
                            winner = re.search("QUALIFIER\d *", str(t)).group()[:-1]
                        except:
                            winner = None

                score = ExtractScore(score)
            scores.append(score)
            winners.append(winner)

        elif t.text.strip() == "": # players & score missing
            if "match data missing;" not in errors:
                errors += "</br>WARNING: match data missing; check every match for errors."
            winner = None
            score = [[0, []], ["BYE"]]
            scores.append(score)
            winners.append(winner)

        elif "\n Bye\n" in t.text:
            all_players = t.find_all('a', {'class': 'scores-draw-entry-box-players-item'})
            qual = ""
            try:
                winner = all_players[0]['data-ga-label']
            except:
                try:
                    winner = re.search("QUALIFIER\d+Q", str(t)).group()[:-1]
                except:
                    try:
                        winner = re.search("QUALIFIER\d *", str(t)).group().strip()
                    except:
                        winner = None

            qual = re.search("QUALIFIER\d+Q", str(t))
            if qual != None:
                winner = qual
            else:
                qual = re.search("QUALIFIER\d+ *", str(t))
                if qual != None:
                    winner = qual.group().strip()
            byes.append(winner)

    def insert_rounds(rounds, from_round):
        sequence = get_sequence(rounds)
        for c, v in enumerate(sequence):
            if v > from_round:
                scores.insert(c, [[0, []], ["BYE"]])
                winners.insert(c, None)

    if qualifying:
        scores = Reorder(players, winners, scores, True)
        matches = FillMatches(matches, winners, scores)
        return matches

    if len(players) == 10 and len(winners) == 12:
        errors += "</br>WARNING: extra matches present; check every match for errors."
        scores = scores[:-3]
        winners = winners[:-3]
        matches = [matches[0][:-1]]
    if len(winners) == 2 * len(matches[0]) and winners.count(None) != len(winners):
        errors += "</br>WARNING: draw has an additional final/3rd place match which needs to be added."
        rounds = int(math.log2(len(winners)))
        del scores[rounds]
        del winners[rounds]
    elif len(winners) == 6:
        insert_rounds(3, 2)
    elif len(winners) == 12 and len(players) == 16:
        insert_rounds(4, 2)
    elif len(winners) == 14:
        insert_rounds(4, 4)
    elif len(winners) == 16:
        insert_rounds(5, 1)
    elif len(winners) == 24 and len(players) == 32:
        insert_rounds(5, 2)
    elif winners.count(None) >= len(winners) - (2 if len(winners) < 64 else 5): # empty draw
        if len(matches[0]) in [9, 17]:
            matches = matches_corrected
        matches = [[f + [[[0, []], ["INIT"]]] for f in matches[0]]]
        matches = AddMissingRounds(matches, doubles)
        errors += "</br>WARNING: one or more rounds missing; check every round for errors."
        return matches

    # for c in range(len(scores)):
    #     print (winners[c], scores[c])

    if winners.count(None) == 1 and len(byes) == 1:
        winners[winners.index(None)] = byes[0]

    scores = Reorder(players, winners, scores, False)
    matches = FillMatches(matches, winners, scores)
    return matches

def ScrapeTournamentATP(url, data):
    global format
    global errors
    errors = ""
    format = None

    if url != None:
        soup, driver = GetSoupSelenium(url, None)
    else:
        soup = GetSoup(data, True)

    unavailable = soup.find('h3', {'class':'not-found-404'})
    if unavailable != None:
        return None, None, None, None, None, None

    typelink = soup.find('a', {'class':'icon icon-blank current'})
    if typelink == None:
        typelink = soup.find('a', {'class':'icon icon-blank disabled current'})
    if typelink == None:
        return None, None, None, None, None, None
    type = typelink.text.strip()
    doubles = "Doubles" in type
    qual = "Q" in type

    date = soup.find('span', {'class':'tourney-dates'})
    if date:
        date = re.search("\d{4}\.\d{2}\.\d{2}", date.text.strip())
        date = datetime.datetime.strptime(date.group(), "%Y.%m.%d").date()
    else:
        date = re.search("\d{4}\/draws", typelink['href']).group()[:4]
        date = datetime.date(int(date), 1, 1)
    data = ExtractTournament(soup, qualifying=qual, doubles=doubles)
    errors = (errors + "</br>\n" if errors != "" else "")
    return data, format, qual, doubles, date, errors
