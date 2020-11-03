# Name:     Tournament draw generator (enwiki)
# Author:   Somnifuguist (w.wiki/fDy)
# Date:     10-10-2020
# Content:  Generates wikitext for tennis tournament draws

import itertools
from nameparser import HumanName
from num2words import num2words
import re
import sys

sys.path.append('data')
from ClassSupportFunctions import *
from GetFlagEN import GetFlagEN

name_links = {}

def GetNameLink(name):
    # Finds and returns formatted name and wikilinks for given name.
    name = HumanName(name)
    name.capitalize(force=True)
    name = str(name)
    global name_links
    lower = name.strip().lower().replace("-", "").replace(" ", "").replace(".", "") # key for name in dict
    if lower in name_links:
        return name_links[lower]
    soup = GetSoup("https://en.wikipedia.org/wiki/" + name.replace(" ", "_"), False).text
    wikitext = name
    tennis = ["International Tennis Federation", "Prize money", "Grand Slam", "tennis career", "Wikipedia does not have", "may refer to", "WTA", "ITF", "ATP"]
    pipe = False
    if soup != None:
        if any([f in soup for f in tennis]): # player article exists, or no article exists
            if "Redirected from" in soup:
                soup = GetSoup(soup, True)
                title = str(soup.title.string).replace(" - Wikipedia", "").strip()
                wikitext = title
                pipe = True # if name is redirect, pipes wikilink to avoid anachronist names, e.g. using "Margaret Court" instead of "Margaret Smith" before she married.
        else: # article exists for name but for different person
            wikitext = name + " (tennis)"
            pipe = True
    wikilink = "[[" + wikitext + ("|" + name if pipe else "") + "]]"
    split_name = name.split(" ")
    abbr_name = "-".join(f[0] for f in split_name[0].split("-")) + " " + " ".join(split_name[1:]) # reduce name to first name initials + last name, e.g. "J-L Struff"
    abbr_wikilink = "[[" + wikitext + "|" + abbr_name + "]]"
    name_links[lower] = [wikilink, abbr_wikilink]
    return name_links[lower]

class Page():
    def __init__(self):
        self.text = [] # contains the draw wikitext

class Player():
    def __init__(self, player, year):
        self.flag = ""
        if player != None:
            self.flag = GetFlagEN(player[1], year)
        self.name_link = GetNameLink(player[0])
        self.seed = player[2]

class Match():
    def __init__(self, match, sets, year):
        self.parsed = False # match has been checked for retirements, tiebreakers etc.
        self.teams = [[Player(f, year) for f in match[0]], [Player(f, year) for f in match[1]]]
        self.score = match[2]
        self.missing = False
        if len(self.score) == 1:
            self.score.append(["{{nowrap|SCORE MISSING}}", ""])
            self.missing = True
        self.score += [["",""]] * (sets - len(match[2]) + 1) # add empty sets to matches where the full number of sets wasn't needed
        self.winner = self.score[0][0]
        if self.score[0][1] == ["w/o"]:
            self.score[1] = ["", "w/o"] if self.winner else ["w/o", ""] # puts w/o on winner's side
        self.bye = ["BYE"] in self.score
        self.sets = sets

class Tournament():
    def __init__(t, data, format, qual, year):
        global name_links
        name_links = LoadJSON("data/NamesEN.json")
        t.data = []
        t.match_tiebreak = format == 2 # deciding set tiebreak in e.g. 2001 Aus Open Mixed Doubles
        format = 3 if format == 2 else format
        for c, round in enumerate(data):
            sets = 3 if format == 3 or (format == 35 and c < len(data) - 1) or (format == 355 and c < len(data) - 2) else 5 # doesn't handle sets formats like 5353.
            t.data.append([Match(match, sets, year) for match in round])
        t.rounds = len(t.data)
        t.format = format # number of sets in matches, 35 if final has 5 sets
        t.doubles = len(data[0][0][0]) == 2
        t.qual = qual
        t.byes = [["BYE"] in match[2][1] for match in data[0]]
        round_names = ["First Round", "Second Round", "Third Round", "Fourth Round", "Fifth Round", "Quarterfinals", "Semifinals", "Final", "Champion" + ("s" if t.doubles else "")]
        t.round_names = round_names[:t.rounds-1] + ["Qualifying Competition", "Qualified"] if t.qual else round_names[:t.rounds-3] + round_names[-4:] # sometimes called "Qualifying Round"

        SaveJSON("data/NamesEN.json", name_links)

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

    def MakeSeeds(t, p, sections, seed_links):
        # Generates and wikitext for seed section of draw article.
        # If seed_links, link each seed's number to the player's section in draw using {{seeds}}/{{qseeds}} templates.
        page = []
        seeds = {} # [team, round reached, final match retired/withdrew]
        for c, round in enumerate(t.data): # find and add all seeds and their results to seeds dict
            for match in round:
                retiredwithdrew = ""
                if not match.missing:
                    retiredwithdrew = "" if match.bye or str(match.score[0][1][-1]).isdigit() else match.score[0][1][-1]
                for i in range(2):
                    seed = match.teams[i][0].seed
                    if seed != []:
                        if seed[0].isdigit():
                            seeds[int(seed[0])] = [match.teams[i], (c if i != match.winner else c + 1), retiredwithdrew]
        def FindSection(sections, seed):
            # Finds section of draw containing given seed.
            for c, section in enumerate(sections):
                for round in section:
                    for match in round:
                        if (match.teams[0][0].seed != [] and match.teams[0][0].seed[0] == str(seed)) or (match.teams[1][0].seed != [] and match.teams[1][0].seed[0] == str(seed)):
                            return str(c + 1)
            return "0"

        if seeds != {}:
            page += ["", "==Seeds==", "{{columns-list|colwidth=30em|"]
            for l in range(1, max(seeds) + 1):
                number = "# "
                if seed_links and len(sections) >= 4:
                    section = "{{seeds" + ("q" if t.qual else "") + "|" + str(l) + "|" + FindSection(sections, l) + "}}"
                    number = (section if section != 0 else "# ")
                else:
                    seed_links = False
                try: # create text for seed, formatting (bold/italics) depending on result
                    style = ("'''" if seeds[l][1] == t.rounds else "''")
                    reached = t.round_names[seeds[l][1]].replace("Round", "round").replace("Competition", "competition") # upper-case is used in draw templates but not seeds
                    retiredwithdrew = ", retired" if seeds[l][2] == "r" else (", withdrew" if seeds[l][2] == "w/o" else "")
                    name_text = " / ".join([f.flag + " " + f.name_link[0] for f in seeds[l][0]])
                    page += [number + (style if style == "'''" else "") + name_text + " " + (style if style == "''" else "") + "(" + reached + retiredwithdrew + ")" + style]
                except KeyError: # seed not in draw, usually due to withdrawal
                    page += [number + "''(Withdrew)''"]
            page += ["}}"] + (["", "{{Seeds explanation}}"] if seed_links else [])
            p.text = page + p.text

    def MakeQualifiers(t, p):
        # Generates wikitext for qualifiers.
        p.text += ["", "==Qualifiers==", "{{columns-list|colwidth=30em|"]
        for match in t.data[-1]:
            winner = match.winner
            p.text += ["# " + " / ".join([f.flag + " '''" + f.name_link[0] + "'''" for f in match.teams[winner]])]
        p.text += ["}}"]

    def MakeSection(t, p, data, rounds, round_names, format, byes, compact, short_names):
        # Generates wikitext for section of draw, using standard templates like {{16TeamBracket-Tennis3}}.
        # Doesn't accommodate for "|byes=1" added with https://en.wikipedia.org/wiki/Wikipedia:Templates_for_discussion/Log/2017_May_10#Template:16TeamBracket-Compact-Tennis35-Byes.
        p.text += ["{{" + str(2**rounds) + "TeamBracket" + ("-Compact" if compact else "") + "-Tennis" + str(format) + ("-Byes" if byes else "")]
        for c, round in enumerate(round_names):
            p.text += ["| RD" + str(c+1) + "=" + round]
        for j in range(rounds):
            team_no = 1
            for match in data[j]:
                p.text += [""]
                if not match.parsed: # add sup tags if not already added for retirements/tiebreakers
                    for c, set in enumerate(match.score[1:]):
                        if set[-1] == "Retired":
                            match.score[c+1][not match.score[0][0]] += "<sup>r</sup>"
                        elif set != ["", ""] and "w/o" not in set and len(set) == 3 and len(set[2]) == 2:
                            match.score[c+1][0] = set[0] + "<sup>" + set[2][0] + "</sup>"
                            match.score[c+1][1] = set[1] + "<sup>" + set[2][1] + "</sup>"
                    match.parsed = True

                for i in range(2): # add seed, team name/flag, score parameters for each team in given match
                    team = match.teams[i]
                    bold = "'''" if match.winner == i else ""
                    name_text = "<br />&amp;nbsp;".join([(f.flag + " " + (bold + f.name_link[short_names] + bold) if not match.bye else "") for f in team])
                    rd = "| RD" + str(j+1) + "-"
                    p.text += [rd + "seed" + str(team_no) + "=" + ("" if match.bye else ("&amp;nbsp;" if team[0].seed == [] else "/".join(team[0].seed)))]
                    p.text += [rd + "team" + str(team_no) + "=" + (name_text if name_text != "<br />&amp;nbsp;" else "")]

                    for set in range(match.sets):
                        p_score  = "" if match.bye else match.score[set+1][i]
                        won_set = (i == match.score[0][1][set]) if set < len(match.score[0][1]) else 0 # no sets in byes/walkovers
                        p_score = "[" + p_score + "]" if t.match_tiebreak and set == 2 and p_score != "" else p_score # add square brackets for match tiebreak
                        p.text += [rd + "score" + str(team_no) + "-" + str(set+1) + "=" + ("'''" + p_score + "'''" if won_set else p_score)]
                    team_no += 1
        p.text += ["}}"]

    def MakeDraw(t, p, compact, abbr, seed_links):
        if t.qual:
            t.MakeQualifiers(p)
            t.MakeLuckyLosers(p)
            p.text += ["", "==Qualifying draw==", "{{Draw key}}"]
            sections = t.SplitData(len(t.data[-1]), t.rounds)
            for i in range(len(sections)):
                ordinal = num2words(i+1, ordinal=True).capitalize()
                p.text += ["", "===" + ordinal + " qualifier==="] # add section heading before each section
                t.MakeSection(p, data=sections[i], rounds=t.rounds, round_names=t.round_names[:-1], format=t.format, byes=t.byes, compact=compact, short_names=abbr)
        else:
            p.text += ["", "==Draw==", "{{Draw key}}"]
            parts = int((2**t.rounds)/16) # number of sections of 16 players needed
            if parts > 1: # "Finals" section needed
                p.text += ["===Finals==="]
                final_rounds = {5:2, 6:3, 7:3, 8:4} # number of rounds to show in "Finals" section given the number of rounds in the tournament
                final_rounds = final_rounds[t.rounds]
                t.MakeSection(p, data=t.data[-final_rounds:], rounds=final_rounds, round_names=t.round_names[-final_rounds - 1:-1], format=t.format, byes=False, compact=False, short_names=False)
            sections = t.SplitData(parts, 4)
            halves = [["===Top half==="], ["===Bottom half==="]]
            for c, section in enumerate(sections):
                if parts > 1:
                    p.text += halves[c // (parts // 2)] if c % (parts // 2) == 0 else [] # add half heading before each half
                    p.text += ["====Section " + str(c+1) + "===="] if t.rounds > 5 else [] # add section heading before each section
                t.MakeSection(p, data=section, rounds=4, round_names=t.round_names[:4], format=(3 if t.format > 5 else t.format), byes=t.byes, compact=compact, short_names=abbr)
        t.MakeSeeds(p, sections, seed_links)

def TournamentDrawOutputEN(data, date, format, qual, compact, abbr, seed_links):
    p = Page()
    t = Tournament(data=data, format=format, qual=qual, year=date.year)
    t.MakeDraw(p, compact=compact, abbr=abbr, seed_links=seed_links)
    return "\n".join(p.text)
