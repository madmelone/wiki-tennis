# Name:     Tournament draw generator (dewiki)
# Author:   Somnifuguist (w.wiki/fDy)
# Date:     10-10-2020
# Content:  Generates wikitext for tennis tournament draws

from ClassSupportFunctions import *

import itertools
from nameparser import HumanName
from num2words import num2words
import re

name_links = {}

def GetNameLink(name, country):
    # Finds and returns formatted name and wikilinks for given name.
    name = HumanName(name)
    name.capitalize(force=True)
    name = str(name)
    soup = GetSoup("https://de.wikipedia.org/wiki/" + name.replace(" ", "_"), False).text
    wikitext = name
    tennis = ["International Tennis Federation", "Preisgeld", "Grand Slam", "Tenniskarriere", "Diese Seite existiert nicht", "ist der Name folgender Personen", "WTA", "ITF", "ATP"]
    pipe = False
    rus = False
    if soup != None:
        if any([f in soup for f in tennis]): # player article exists, or no article exists
            if "Weitergeleitet von" in soup:
                soup = GetSoup(soup, True)
                title = str(soup.title.string).replace(" - Wikipedia", "").replace(" – Wikipedia", "").strip()
                if len(title.split(" ")) >= 3 and country == "RUS":
                    name = title.split(" ")
                    name = name[0] + " " + " ".join(name[2:])
                    rus = True
                wikitext = title
                pipe = False if not rus else True # If True, then if name is redirect, pipes wikilink to avoid anachronist names, e.g. using "Margaret Court" instead of "Margaret Smith" before she married.
        else: # article exists for name but for different person
            wikitext = name + " (Tennisspieler)"
            pipe = True
    wikilink = ("Ziel=" if not pipe else "") + wikitext + ("|" + name if pipe else "")
    split_name = (name if rus else wikitext).replace(" (Tennisspieler)", "").split(" ")
    abbr_name = ".-".join(f[0] for f in split_name[0].split("-")) + ". " + " ".join(split_name[1:]) # reduce name to first name initials + last name, e.g. "J.-L. Struff"
    abbr_wikilink = wikitext + "|" + abbr_name
    return [name, wikilink, abbr_wikilink]

class Page():
    def __init__(self):
        self.text = [] # contains the draw wikitext

class Player():
    def __init__(self, player):
        global name_links
        countries = LoadJSON("data/CountriesDE.json")
        country = ""
        if player != None:
            country = countries[player[1]] if player[1] in countries else player[1]
        if player[0] not in name_links:
            name_links[player[0]] = GetNameLink(player[0], country)
        self.playertext = {0: "{{" + country + "|" + name_links[player[0]][1] + "}}", 1: "{{" + country + "|" + name_links[player[0]][2] + "}}", 2: "{{" + country + "|" + name_links[player[0]][1] + "}}"}
        length0 = len(name_links[player[0]][1].split("|")[-1].replace("Ziel=", ""))
        length1 = len(name_links[player[0]][2].split("|")[-1])
        if length0 > 10:
            self.playertext[0] = "{{nowrap|" + self.playertext[0] + "}}"
        if length1 > 10:
            self.playertext[1] = "{{nowrap|" + self.playertext[1] + "}}"
        self.seed = [f.replace("Alt", "ALT") for f in player[2]]

class Match():
    def __init__(self, match, sets):
        self.parsed = False # match has been checked for retirements, tiebreakers etc.
        self.teams = [[Player(f) for f in match[0]], [Player(f) for f in match[1]]]
        self.score = match[2]
        for i in range((sets - len(match[2]) + 1)):
            self.score += [["",""]] # add empty sets to matches where the full number of sets wasn't needed
        self.winner = self.score[0][0]
        if self.score[0][1] == ["w/o"]:
            self.score[1] = ["", "w."] if self.winner else ["w.", ""] # puts w/o on winner's side
            self.score[2] = ["", "o."] if self.winner else ["o.", ""]
        self.bye = ["BYE"] in self.score
        self.sets = sets

class Tournament():
    def __init__(t, data, format, qual, year):
        global name_links
        name_links = LoadJSON("data/NameLinksDE.json")
        t.data = []
        t.match_tiebreak = format == 2 # deciding set tiebreak in e.g. in 2001 Aus Open Mixed Doubles
        format = 3 if format == 2 else format
        for c, round in enumerate(data):
            sets = 3 if format == 3 or (format == 35 and c < len(data) - 1) or (format == 355 and c < len(data) - 2) else 5 # doesn't handle sets formats like 5353.
            t.data.append([Match(match, sets) for match in round])
        t.rounds = len(t.data)
        t.format = format # number of sets in matches, 35 if final has 5 sets
        t.doubles = len(data[0][0][0]) == 2
        t.qual = qual
        t.byes = sum([match[2][1][0] == "BYE" for match in data[0]]) > 0
        round_names = ["Erste Runde", "Zweite Runde", "Dritte Runde", "Vierte Runde", "Achtelfinale", "Viertelfinale", "Halbfinale", "Finale", "Sieg"]
        t.round_names = round_names[:t.rounds-1] + ["Qualifikationsrunde", "qualifiziert"] if t.qual else round_names[:t.rounds-4] + round_names[-5:]
        t.lucky_losers = []
        t.template_size = 32 if t.rounds == 5 else 8 if (t.rounds == 6 and t.doubles) else 16 # template size for main draws
        SaveJSON("data/NameLinksDE.json", name_links)

    def SplitData(t, n, r):
        # Splits first r rounds of data into n equal sections.
        SplitData = []
        for i in range(n):
            part = []
            for j in range(r):
                matches = int(len(t.data[j])/n)
                part.append(t.data[j][i*matches:(i+1)*matches])
            SplitData.append(part)
        return SplitData

    def MakeSeeds(t, p, sections):
        # Generates and wikitext for seed section of draw article.
        page = []
        seeds = {} # [team, round reached, final match retired/withdrew]
        for c, round in enumerate(t.data): # find and add all seeds and their results to seeds dict
            for match in round:
                for i in range(2):
                    seed = match.teams[i][0].seed
                    if seed != []:
                        if seed[0].isdigit():
                            seeds[int(seed[0])] = [match.teams[i], (c if i != match.winner else c + 1)]

        if seeds != {}:
            page += ["", "== Setzliste ==", "<onlyinclude>{{Setzliste", "| Anzahl = " + str(max(seeds)), "| Modus = " + ("Doppel" if t.doubles else "Herreneinzel")]
            for l in range(1, max(seeds) + 1):
                letters = ["A", "B"]
                try:
                    for c, f in enumerate(seeds[l][0]):
                        page += ["| " + str(l) + letters[c] + " = " + f.playertext[2]]
                    reached = t.round_names[seeds[l][1]].replace("Erste ", "1. ").replace("Zweite ", "2. ").replace("Dritte ", "3. ").replace("Vierte ", "4. ")
                    page += ["| " + str(l) + "R = " + reached]
                except KeyError:
                    page += ["| " + str(l) + "A = \n| " + str(l) + "B = \n|" + str(l) + "R = Rückzug"]
            page += ["}}</onlyinclude>", "{{Tennisturnier Zeichenerklärung}}"]
            p.text = page + p.text

    def MakeQualifiers(t, p):
        # Generates wikitext for qualifiers.
        p.text += ["", "==Qualifikation==", '{| class="wikitable"', '|-', '! Qualifikanten']
        for match in t.data[-1]:
            winner = match.winner
            players = ["| " + f.playertext[2] for f in match.teams[winner]]
            p.text += ["|-\n" + "\n".join(players)]
        p.text += ["|}"]

    def MakeSection(t, p, data, rounds, round_names, format, byes, compact, abbr):
        # Generates wikitext for section of draw, using standard templates like {{Turnierplan16-3}}.
        p.text += ["{{" + "Turnierplan" + str(2**rounds) + ("-kompakt-" if compact else "-") + str(format) + ("-Freilos" if byes else "")]
        for c, round in enumerate(round_names):
            p.text += ["| RD" + str(c+1) + "=" + round]
        for j in range(rounds):
            team_no = 1
            for match in data[j]:
                p.text += [""]
                retired = False
                if not match.parsed: # add sup tags if not already added for retirements/tiebreakers
                    for c, set in enumerate(match.score[1:]):
                        if set[-1] == "Retired" and not retired:
                            if set == ['0', '0', 'Retired']:
                                retiree = match.score[0][0]
                                match.score[c+1] = ["r" if retiree else "", "" if retiree else "r"]
                            elif c + 1 == len(match.score[1:]):
                                match.score[c+1][not match.score[0][0]] += "r"
                            else:
                                match.score[c+2][not match.score[0][0]] += "r"
                            retired = True
                        elif set != ["", ""] and "." not in set and len(set) == 3 and len(set[2]) == 2:
                            if set[0] == "6":
                                match.score[c+1][0] = set[0] + "<sup>" + set[2][0] + "</sup>"
                            else:
                                match.score[c+1][1] = set[1] + "<sup>" + set[2][1] + "</sup>"
                    match.parsed = True

                for i in range(2): # add seed, team name/flag, score parameters for each team in given match
                    team = match.teams[i]
                    bold = "'''" if match.winner == i else ""
                    name_text = "<br />&amp;nbsp;".join([(bold + f.playertext[abbr] + bold if not match.bye else "") for f in team])
                    rd = "| RD" + str(j+1) + "-"
                    num = "0" + str(team_no) if team_no < 10 and (rounds > 3 or compact) else str(team_no)
                    p.text += [rd + "seed" + num + "=" + ("" if match.bye else ("&amp;nbsp;" if team[0].seed == [] else "/".join(team[0].seed)))]
                    p.text += [rd + "team" + num + "=" + (name_text if name_text != "<br />&amp;nbsp;" else "")]

                    for set in range(match.sets):
                        p_score  = "" if match.bye else match.score[set+1][i]
                        won_set = (i == match.score[0][1][set]) if set < len(match.score[0][1]) else 0 # no sets in byes/walkovers
                        p_score = "[" + p_score + "]" if t.match_tiebreak and set == 2 and p_score != "" else p_score # add square brackets for match tiebreak
                        p.text += [rd + "score" + num + "-" + str(set+1) + "=" + ("'''" + p_score + "'''" if won_set else p_score)]
                    team_no += 1
        p.text += ["}}"]

    def MakeDraw(t, p, compact, abbr):
        if t.qual:
            p.text += ["", "== Ergebnisse =="]
            sections = t.SplitData(len(t.data[-1]), t.rounds)
            for i in range(len(sections)): # no logical section headings
                ordinal = num2words(i+1, ordinal=True).capitalize()
                t.MakeSection(p, data=sections[i], rounds=t.rounds, round_names=t.round_names[:-1], format=t.format, byes=t.byes, compact=compact, abbr=abbr)
        else:
            p.text += ["", "== Ergebnisse =="]
            parts = int((2**t.rounds)/t.template_size) # number of sections needed
            if parts > 1: # "Finals" section needed
                if t.doubles:
                    final_rounds = {5:2, 6:3, 7:3, 8:4}
                else:
                    final_rounds = {5:2, 6:2, 7:3, 8:4} # number of rounds to show in "Finals" section given the number of rounds in the tournament
                final_rounds = final_rounds[t.rounds]
                p.text += ["===" + ", ".join(t.round_names[-(final_rounds+1):-1]) + "==="]
                t.MakeSection(p, data=t.data[-final_rounds:], rounds=final_rounds, round_names=t.round_names[-final_rounds - 1:-1], format=t.format, byes=False, compact=final_rounds==4, abbr=False)
            section_rounds = 5 if t.template_size == 32 else 3 if t.template_size == 8 else 4
            sections = t.SplitData(parts, section_rounds)
            halves = ["Obere Hälfte", "Untere Hälfte"]
            half_curr = ""
            index_curr = 0
            for c, section in enumerate(sections):
                if parts > 1:
                    half = halves[c // (parts // 2)] if c % (parts // 2) == 0 else ""
                    half_curr = half if half != "" else half_curr
                    p.text += ["===" + half + "==="] if half != "" and t.rounds > 5 else []
                    p.text += ["====" + half_curr + " " + str(int(index_curr%(parts/2))+1) + "===="]  # add section heading before each section
                    index_curr += 1
                t.MakeSection(p, data=section, rounds=section_rounds, round_names=t.round_names[:section_rounds], format=(3 if t.format > 5 else t.format), byes=t.byes, compact=compact, abbr=abbr)
        t.MakeSeeds(p, sections)

def TournamentDrawOutputDE(data, year, format, qual, compact, abbr):
    p = Page()
    t = Tournament(data=data, format=format, qual=qual, year=year)
    t.MakeDraw(p, compact=compact, abbr=abbr)
    return "\n".join(p.text)
