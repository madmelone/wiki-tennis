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

# new_names = ""
corrections = []
wiki_pages = []

def GetNameCorrections():
    # Loads corrections from page
    page = "User:Somnifuguist/NameCorrections"
    change = [{}, {}] # {full name corrections}, {shortened name corrections}
    return change
    try:
        wikitext = GetSoup("https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&&titles=" + page, 'json')['query']['pages']['68204305']['revisions'][0]['*']
    except:
        return change

    # {full name corrections}[player] = [full name link, shortened name link]
    shortened = False
    for d in wikitext.split("\n* "):
        if "Shortened" in d:
            shortened = True
        if not shortened:
            if not any([f not in d for f in [" → ", "[[", "]]"]]) and "[[]]" not in d:
                d = [f.strip() for f in d.replace("[", "").replace("]", "").split(" → ")]
                name = re.sub(r" \(.*\)", "", d[1])
                key = LowerName(d[0])
                if name != d[1]: # name is disambiguated
                    long = d[1] + "|" + name
                else:
                    long = "[[" + d[1] + "]]"
                short = "[[" + d[1] + "|" + "-".join(f[0] for f in name.split(" ")[0].split("-")) + " " + " ".join(name.split(" ")[1:]) + "]]"
                change[0][key] = [long, short]
        else: # shortened name correction
            if "<!--" not in d and d.strip("* →") != "":
                d = [f.strip() for f in d.split(" → ")]
                change[1][d[0]] = d[1]
    return change

def NormaliseName(name):
    name = name.replace(". ", ".").replace(".", ". ")
    split_name = name.split(" ")
    mixed_case = [f for f in split_name if (not f.islower() and not f.isupper()) or f.islower()]
    surname_index = 0
    if mixed_case != []:
        surname_index = split_name.index(mixed_case[-1]) + 1
    first_names = " ".join(split_name[:surname_index])
    surname = HumanName(" ".join(split_name[surname_index:]))
    surname.capitalize(force=True)
    name = (first_names + " " + str(surname)).strip()
    return name

## bulk download of player wikipedia pages rather than repeated page requests
# def FetchWikiPages(data):
#     return
#     global name_links
#     global wiki_pages
#
#     players = [[g[0] for g in f[0]] for f in data[0]] + [[g[0] for g in f[1]] for f in data[0]]
#     players = [j for i in players for j in i]
#     players = [NormaliseName(f) for f in players]
#     keys = [LowerName(f) for f in players]
#     # players = [f for f in players if f not in name_links]
#     title_str = "|".join(players[:3])
#     content = GetSoup(f"https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&rvslots=*&format=json&&titles=" + title_str, 'json')
#     # page_text = GetSoup("https://en.wikipedia.org/wiki/" + name.replace(" ", "_"), False).text"

def GetNameLink(name):
    # Finds and returns formatted name and wikilinks for given name.
    global name_links
    global corrections
    global new_names

    if "qualifier" in name.lower() or name.lower() in ["bye", "player missing"]:
        return [name, name]

    if name == "":
        return ["", ""]
    # old_name = name
    name = NormaliseName(name)

    key = LowerName(name) # key for name in names dict
    if key in name_links:
        links = name_links[key]
    else:
        print ("\t", key)
        page_text = GetSoup("https://en.wikipedia.org/wiki/" + name.replace(" ", "_"), False).text
        page_text = "" if page_text == None else page_text
        title = name # player's article's title
        player_page = ["International Tennis Federation", "Prize money", "Grand Slam", "tennis career", "Wikipedia does not have", "WTA", "ITF", "ATP"]
        disamb_page = ["may refer to", "may also refer to"]
        disamb = " (tennis)"
        is_disamb = False
        pipe = False # pipe [[title|name]] instead of [[title]].
        if "Redirected from" in page_text: # redirected
            soup = GetSoup(page_text, True)
            title = str(soup.title.string).replace(" - Wikipedia", "").replace(" – Wikipedia", "").strip()
            if "tennis" in title or any([f in page_text for f in disamb_page]): # redirected to disambiguated page, or disamb page
                is_disamb = True
                pipe = True
                title = re.sub(r" \(.*\)", "", title)
                name = title
            # pipe = True # display English spelling/maiden name (e.g. "Margaret Court" instead of "Margaret Smith" before she married).

        if (not any([f in page_text for f in player_page]) or any([f in page_text for f in disamb_page]) and page_text != ""): # article exists for name but for different person, or disamb page
            is_disamb = True
            pipe = True

        wikilink = "[[" + title + (disamb if is_disamb else "") + ("|" + name if pipe else "") + "]]"
        split_name = title.split(" ")
        abbr_name = "-".join(f[0] for f in split_name[0].split("-")) + " " + " ".join(split_name[1:]) # reduce name to first name initials + last name, e.g. "J.-L. Struff"
        abbr_wikilink = "[[" + title + (disamb if is_disamb else "") + "|" + abbr_name + "]]"
        name_links[key] = [wikilink, abbr_wikilink]
        links = name_links[key]

        # # add entry to new names list
        # exists = "Diese Seite existiert nicht" not in page_text
        # disamb = disamb if is_disamb else ""
        # link = f'<a href="https://en.wikipedia.org/wiki/{title}{disamb}" style="color:{"blue" if exists else "red"};">{title}{disamb}</a>'
        # new_names += f"\t<li>{old_name} → [[{abbr_wikilink.replace(title + disamb, link)}]]</li>"

    if "|" in links[0]:
        corrections_key = links[0][:links[0].index("|")]
    else:
        corrections_key = links[0]
    corrections_key = LowerName(corrections_key).strip("[]")
    if corrections_key in corrections[0]: # name has correction
        links = corrections[0][corrections_key]
    abbr = links[1][links[1].index("|") + 1:] if "|" in links[1] else links[1]
    abbr = abbr.strip("[]")
    if abbr in corrections[1]:
        links[1] = links[1][:links[1].index("|") + 1] + corrections[1][abbr] + "]]"
    return links

class Page():
    def __init__(self):
        self.text = [] # contains the draw wikitext
        self.error = ""

class Player():
    def __init__(self, player, year):
        self.flag = ""
        if player[2] != ['BYE']:
            if player != None:
                self.flag = GetFlagEN(player[1], year)
            self.name_link = GetNameLink(player[0])
            self.seed = player[2]
        else:
            self.flag = ""
            self.name_link = ["", ""]
            self.seed = [""]

class Match():
    def __init__(self, match, sets, year):
        # print (match)
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
        self.bye = ["BYE"] in self.score or ["INIT"] in self.score
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
        t.init = ["INIT"] in data[0][0][2]
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
                retiredwithdrewdefaulted = ""
                if not match.missing:
                    retiredwithdrewdefaulted = "" if match.bye or str(match.score[0][1][-1]).isdigit() else match.score[0][1][-1]
                for i in range(2):
                    seed = match.teams[i][0].seed
                    if seed != []:
                        if seed[0].isdigit():
                            seeds[int(seed[0])] = [match.teams[i], (c if i != match.winner else c + 1), retiredwithdrewdefaulted]
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
                    retiredwithdrewdefaulted = ", retired" if seeds[l][2] == "r" else (", withdrew" if seeds[l][2] == "w/o" else (", defaulted" if seeds[l][2] == "d" else ""))
                    name_text = " / ".join([f.flag + " " + f.name_link[0] for f in seeds[l][0]])
                    if t.init:
                        page += [number + name_text]
                    else:
                        page += [number + (style if style == "'''" else "") + name_text + " " + (style if style == "''" else "") + "(" + reached + retiredwithdrewdefaulted + ")" + style]
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
                retired = False
                default = False
                if not match.parsed: # add sup tags if not already added for retirements/tiebreakers
                    for c, set in enumerate(match.score[1:]):
                        if set[-1] == "Retired":
                            match.score[c+1][not match.score[0][0]] += "<sup>r</sup>"
                            retired = True
                        elif set[-1] == "Default":
                            match.score[c+1][not match.score[0][0]] += "<sup>d</sup>"
                            default = True
                        elif set != ["", ""] and "w/o" not in set and len(set) == 3 and len(set[2]) == 2:
                            match.score[c+1][0] = set[0] + "<sup>" + set[2][0] + "</sup>"
                            match.score[c+1][1] = set[1] + "<sup>" + set[2][1] + "</sup>"
                    match.parsed = True

                for i in range(2): # add seed, team name/flag, score parameters for each team in given match
                    team = match.teams[i]
                    bold = "'''" if match.winner == i and not t.init else ""
                    init_bye = any("BYE" in f.name_link[short_names] for f in team)
                    name_text = " <br />".join([(f.flag + " " + (bold + f.name_link[short_names] + bold) if (not match.bye or (t.init and not init_bye)) else "") for f in team])
                    rd = "| RD" + str(j+1) + "-"
                    p.text += [rd + "seed" + str(team_no) + "=" + ("" if match.bye and not t.init else ("&amp;nbsp;" if team[0].seed == [] else "/".join(team[0].seed)))]
                    p.text += [rd + "team" + str(team_no) + "=" + (name_text if name_text != " <br />" else "")]
                    for set in range(match.sets):
                        p_score  = "" if match.bye else match.score[set+1][i]
                        won_set = (i == match.score[0][1][set]) if set < len(match.score[0][1]) and not (set == len(match.score[0][1]) - 1 and (default or retired)) else 0 # no sets in byes/walkovers

                        match_tiebreak = t.match_tiebreak
                        if t.match_tiebreak and set == 2 and len(match.score) > 1 and match.score[set+1][0].isdigit() and match.score[set+1][1].isdigit():
                            if max(int(match.score[set+1][0]), int(match.score[set+1][1])) < 10:
                                match_tiebreak = False
                                if "match tiebreak" not in p.error:
                                    p.error += "\nERROR: Mix of match tiebreak scores and non-match tiebreak scores. Check all scores.\n"
                        p_score = "[" + p_score + "]" if match_tiebreak and set == 2 and p_score != "" else p_score # add square brackets for match tiebreak
                        p.text += [rd + "score" + str(team_no) + "-" + str(set+1) + "=" + ("'''" + p_score + "'''" if won_set else p_score)]
                    team_no += 1
        p.text += ["}}"]

    def MakeDraw(t, p, compact, abbr, seed_links):
        if t.qual:
            t.MakeQualifiers(p)
            # t.MakeLuckyLosers(p)
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
            if parts == 0:
                t.MakeSection(p, data=t.data[-len(t.data):], rounds=len(t.data), round_names=["First Round"] + t.round_names[-len(t.data):-1], format=t.format, byes=False, compact=False, short_names=False)
            else:
                sections = t.SplitData(parts, 4)
                halves = [["===Top half==="], ["===Bottom half==="]]
                for c, section in enumerate(sections):
                    if parts > 1:
                        p.text += halves[c // (parts // 2)] if c % (parts // 2) == 0 else [] # add half heading before each half
                        p.text += ["====Section " + str(c+1) + "===="] if t.rounds > 5 else [] # add section heading before each section
                    t.MakeSection(p, data=section, rounds=4, round_names=t.round_names[:4], format=(3 if t.format > 5 else t.format), byes=t.byes, compact=compact, short_names=abbr)
                t.MakeSeeds(p, sections, seed_links)

def initialize(data):
    global name_links
    global corrections
    global new_names
    name_links = LoadJSON("data/NamesEN.json")
    corrections = GetNameCorrections()
    # FetchWikiPages(data)
    # new_names = "<h5>New names encountered:</h5>\n<ul>"

def TournamentDrawOutputEN(data, date, format, qual, compact, abbr, seed_links):
    initialize(data)
    # global new_names
    # empty_names = new_names
    p = Page()
    t = Tournament(data=data, format=format, qual=qual, year=date.year)
    t.MakeDraw(p, compact=compact, abbr=abbr, seed_links=seed_links)
    # names = "" if new_names == empty_names else f"{new_names}</ul>"
    return "", p.error + "\n".join(p.text)
