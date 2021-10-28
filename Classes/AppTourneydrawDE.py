# Name:     Tournament draw generator (dewiki)
# Author:   Somnifuguist
# Date:     10-10-2020
# Content:  Generates wikitext for tennis tournament draws

import itertools
from nameparser import HumanName
from num2words import num2words
import re
import sys

sys.path.append('data')
from ClassSupportFunctions import *
from GetFlagDE import GetFlagDE

name_links = {}
static_name_links = {}
new_names = ""
corrections = []

def GetNameCorrections():
    # Loads corrections from https://de.wikipedia.org/wiki/Benutzer:Siebenschl%C3%A4ferchen/Turnier-Generator
    change = [{}, {}] # {full name corrections}, {shortened name corrections};
    page = "Benutzer:Siebenschl%C3%A4ferchen/Turnier-Generator"
    try:
        wikitext = GetSoup("https://de.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&&titles=" + page, 'json')['query']['pages']['68204305']['revisions'][0]['*']
    except:
        return change

    # {full name corrections}[player] = [[full link, shortened link], [full link for Russian, shortened link for Russian]]; Russian links are only used by GetNameLink() if player is Russian
    shortened = False
    for d in wikitext.split("\n* "):
        if "Shortened" in d:
            shortened = True
        if not shortened:
            if " → " in d and "[[" in d and "]]" in d and not "[[]]" in d:
                d = [f.strip() for f in d.replace("[", "").replace("]","").split(" → ")]
                name = re.sub(r" \(.*\)", "", d[1])
                key = LowerName(d[0])
                if name != d[1]: # name is disambiguated
                    long = d[1] + "|" + name
                else:
                    long = "Ziel=" + d[1]
                long_rus = long
                if len(name.split(" ")) >= 3:
                    rus = name.split(" ")
                    long_rus = d[1] + "|" + rus[0] + " " + " ".join(rus[2:])
                short = d[1] + "|" + ".-".join(f[0] for f in name.split(" ")[0].split("-")) + ". " + " ".join(name.split(" ")[1:])
                short_rus = short
                if long_rus != long:
                    rus = long_rus.split("|")[1]
                    short_rus = d[1] + "|" + ".-".join(f[0] for f in rus.split(" ")[0].split("-")) + ". " + " ".join(rus.split(" ")[1:])
                change[0][key] = [[long, short], [long_rus, short_rus]]
        else: # shortened name correction
            if "<!--" not in d and d.strip("* →") != "":
                d = [f.strip() for f in d.split(" → ")]
                change[1][d[0]] = d[1]
    return change

def GetNameLink(name, country, mens):
    # Finds and returns formatted name and wikilinks for given name.
    if name == "":
        return ["", ""]
    elif "qualifier" in name.lower() or name.lower() in ["bye", "player missing"]:
        return ["Ziel="+name, "Ziel="+name]

    old_name = name
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
    is_rus = any([f in country for f in ["RUS", "SUN", "URS"]]) # assume player uses Russian naming customs

    global name_links
    global static_links
    global corrections
    global new_names

    key = LowerName(name) # key for name in names dict
    if key in static_name_links:
        links = static_name_links[key]
    elif key in name_links:
        links = name_links[key]
    else:
        page_text = GetSoup("https://de.wikipedia.org/wiki/" + name.replace(" ", "_"), False).text
        page_text = "" if page_text == None else page_text
        title = name # player's article's title
        player_page = ["International Tennis Federation", "Preisgeld", "Grand Slam", "Tenniskarriere", "Diese Seite existiert nicht", "WTA", "ITF", "ATP"]
        disamb_page = ["Kategorie:Begriffsklärung", "Dies ist eine Begriffsklärungsseite zur Unterscheidung mehrerer mit demselben Wort bezeichneter Begriffe.", "ist der Name folgender Personen:"]
        disamb = " (Tennisspieler)" if mens else " (Tennisspielerin)"
        is_disamb = False
        pipe = False # pipe [[title|name]] instead of [[title]].

        if "Weitergeleitet von" in page_text: # redirected
            soup = GetSoup(page_text, True)
            title = str(soup.title.string).replace(" - Wikipedia", "").replace(" – Wikipedia", "").strip()
            if "Tennisspieler" in title or any([f in page_text for f in disamb_page]): # redirected to disambiguated page, or disamb page
                is_disamb = True
                pipe = True
                title = re.sub(r" \(.*\)", "", title)
                name = title
            # pipe = True # display English spelling/maiden name (e.g. "Margaret Court" instead of "Margaret Smith" before she married).

        rus_patronym = len(title.split(" ")) >= 3 and is_rus

        if rus_patronym: # russian name
            name = title.split(" ")
            name = name[0] + " " + " ".join(name[2:])
            pipe = True

        if (not any([f in page_text for f in player_page]) or any([f in page_text for f in disamb_page]) and page_text != ""): # article exists for name but for different person, or disamb page
            is_disamb = True
            pipe = True

        wikilink = ("Ziel=" if not pipe else "") + title + (disamb if is_disamb else "") + ("|" + name if pipe else "")
        split_name = (name if rus_patronym else title).split(" ")
        abbr_name = ".-".join(f[0] for f in split_name[0].split("-")) + ". " + " ".join(split_name[1:]) # reduce name to first name initials + last name, e.g. "J.-L. Struff"
        abbr_wikilink = title + (disamb if is_disamb else "") + "|" + abbr_name
        name_links[key] = [wikilink, abbr_wikilink]
        links = name_links[key]

        # add entry to new names list
        exists = "Diese Seite existiert nicht" not in page_text
        disamb = disamb if is_disamb else ""
        link = f'<a href="https://de.wikipedia.org/wiki/{title}{disamb}" style="color:{"blue" if exists else "red"};">{title}{disamb}</a>'
        new_names += f"\t<li>{old_name} → [[{abbr_wikilink.replace(title + disamb, link)}]]</li>"

    if "|" in links[0]:
        corrections_key = links[0][:links[0].index("|")]
    else:
        corrections_key = links[0]

    corrections_key = LowerName(corrections_key).replace("ziel=", "")
    if corrections_key in corrections[0]: # name has correction
        links = corrections[0][corrections_key][is_rus]
    abbr = links[1][links[1].index("|") + 1:] if "|" in links[1] else links[1]
    if abbr in corrections[1]:
        links[1] = links[1][:links[1].index("|") + 1] + corrections[1][abbr]
    return links

class Page():
    def __init__(self):
        self.text = [] # contains the draw wikitext
        self.error = ""

class Player():
    def __init__(self, player, date, mens):
        if player != None:
            country = ""
            if player[1] != "":
                country = GetFlagDE(player[1], date)
            name_link = GetNameLink(player[0], country, mens)
            # 0: full name, 1: shortened name, 2: full name without nowrap (for seeds)
            def country_temp(country, name):
                return "{{" + country + "|" + name + "}}" if country != "" else "[[" + name + "]]"
            self.playertext = {0: country_temp(country, name_link[0]), 1: country_temp(country, name_link[1]), 2: country_temp(country, name_link[0])}
            length0 = len(name_link[0].split("|")[-1].replace("Ziel=", ""))
            length1 = len(name_link[1].split("|")[-1])
            if length0 > 10: # need to prevent name wrapping in draw bracket
                self.playertext[0] = "{{nowrap|" + self.playertext[0] + "}}"
            if length1 > 10:
                self.playertext[1] = "{{nowrap|" + self.playertext[1] + "}}"
            self.seed = [f.replace("Alt", "ALT") for f in player[2]]
        else:
            text = "{{nowrap|PLAYER MISSING}}"
            self.playertext = {0: text, 1: text, 2: text}
            self.seed = [""]

class Match():
    def __init__(self, match, sets, date, mens):
        self.parsed = False # match has been checked for retirements, tiebreakers etc.
        self.teams = [[Player(f, date, mens) for f in match[0]], [Player(f, date, mens) for f in match[1]]]
        self.score = match[2]
        if len(self.score) == 1:
            self.score.append(["{{nowrap|SCORE MISSING}}", ""])
        for i in range((sets - len(match[2]) + 1)):
            self.score += [["",""]] # add empty sets to matches where the full number of sets wasn't needed
        self.winner = self.score[0][0]
        if self.score[0][1] == ["w/o"]:
            self.score[1] = ["", "w."] if self.winner else ["w.", ""] # puts w/o on winner's side
            self.score[2] = ["", "o."] if self.winner else ["o.", ""]
        self.bye = ["BYE"] in self.score
        self.missing_final = False # score is missing for final
        self.sets = sets

class Tournament():
    def __init__(t, data, mens, format, qual, date):
        global name_links
        t.data = []
        t.match_tiebreak = format == 2 # deciding set tiebreak in e.g. in 2001 Aus Open Mixed Doubles
        format = 3 if format == 2 else format
        for c, round in enumerate(data):
            sets = 3 if format == 3 or (format == 35 and c < len(data) - 1) or (format == 355 and c < len(data) - 2) else 5 # doesn't handle sets formats like 5353.
            t.data.append([Match(match, sets, date, mens) for match in round])
            if c == len(data) - 1 and t.data[-1][0].bye:
                t.data[-1][0].missing_final = True
        t.rounds = len(t.data)
        t.format = format # number of sets in matches, 35 if final has 5 sets
        t.doubles = len(data[0][0][0]) == 2
        t.qual = qual
        t.byes = sum([match[2][1][0] == "BYE" for match in data[0]]) > 0
        t.init = ["INIT"] in data[0][0][2]
        round_names = ["Erste Runde", "Zweite Runde", "Dritte Runde", "Vierte Runde", "Achtelfinale", "Viertelfinale", "Halbfinale", "Finale", "Sieg"]
        nonfinal = t.rounds < 5 # tournament starts with first round instead of final
        t.round_names = round_names[:t.rounds-1] + ["Qualifikationsrunde", "qualifiziert"] if t.qual else round_names[:t.rounds-4+nonfinal] + round_names[-5+nonfinal:]
        t.template_size = 32 if t.rounds == 5 else 8 if ((t.rounds == 6 and t.doubles) or t.rounds == 3) else 16 # template size for main draws
        t.template = None
        t.qual_index = 0
        SaveJSON("data/NamesDE.json", name_links)

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
                            seeds[int(seed[0])] = [match.teams[i], (c if i != match.winner or match.missing_final else c + 1)]

        if seeds != {}:
            page += ["", ("== Einzel ==" if not t.doubles else "== Doppel =="), "=== Setzliste ===", "{{Setzliste", "| Anzahl = " + str(max(seeds)), "| Modus = " + ("Doppel" if t.doubles else "Herreneinzel")]
            for l in range(1, max(seeds) + 1):
                letters = ["A", "B"]
                try:
                    for c, f in enumerate(seeds[l][0]):
                        page += ["| " + str(l) + letters[c] + " = " + f.playertext[2]]
                    reached = t.round_names[seeds[l][1]].replace("Erste ", "1. ").replace("Zweite ", "2. ").replace("Dritte ", "3. ").replace("Vierte ", "4. ")
                    page += ["| " + str(l) + "R = " + reached]
                except KeyError:
                    page += ["| " + str(l) + "A = \n| " + (str(l) + "B = \n| " if t.doubles else "") + str(l) + "R = Rückzug"]
            page += ["}}", "{{Tennisturnier Zeichenerklärung}}"]
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
        if not t.qual or t.qual_index == 0:
            template = ("{{Turnierplan" + str(2**rounds) + ("-kompakt-" if compact else "-") + str(format) + ("-Freilos" if byes else "")) if t.template == None else t.template
            p.text += [template]
        for c, round in enumerate(round_names):
            p.text += ["| RD" + str(c+1) + "=" + round]
        for j in range(rounds):
            team_no = 1 if not t.qual else 2**(rounds-j) * t.qual_index + 1
            for match in data[j]:
                p.text += [""]
                retired = False
                default = False
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
                        if set[-1] == "Default" and not default:
                            if set == ['0', '0', 'Default']:
                                defaultee = match.score[0][0]
                                match.score[c+1] = ["d" if defaultee else "", "" if defaultee else "d"]
                            elif c + 1 == len(match.score[1:]):
                                match.score[c+1][not match.score[0][0]] += "d"
                            else:
                                match.score[c+2][not match.score[0][0]] += "d"
                            default = True
                        elif set != ["", ""] and "." not in set and len(set) == 3 and len(set[2]) == 2:
                            if set[0] == "6":
                                match.score[c+1][0] = set[0] + "<sup>" + set[2][0] + "</sup>"
                            else:
                                match.score[c+1][1] = set[1] + "<sup>" + set[2][1] + "</sup>"
                    match.parsed = True

                for i in range(2): # add seed, team name/flag, score parameters for each team in given match
                    team = match.teams[i]
                    bold = "'''" if match.winner == i and not t.init else ""
                    name_text = "<br />&amp;nbsp;".join([(bold + f.playertext[abbr] + bold if not match.bye else "") for f in team])
                    rd = "| RD" + str(j+1) + "-"
                    num = "0" + str(team_no) if team_no < 10 and (rounds > 3 or compact) else str(team_no)
                    p.text += [rd + "seed" + num + "=" + ("" if match.bye else ("&amp;nbsp;" if team[0].seed == [] else (team[0].seed[0] if len(team[0].seed) == 1 else "{{nowrap|" + team[0].seed[0] + " <small>" + team[0].seed[1] + "</small>}}")))]
                    p.text += [rd + "team" + num + "=" + (name_text if name_text != "<br />&amp;nbsp;" else "")]

                    match_tiebreak = t.match_tiebreak
                    if t.match_tiebreak and set == 2 and len(match.score) > 1 and match.score[set+1][0].isdigit() and match.score[set+1][1].isdigit():
                        if max(int(match.score[set+1][0]), int(match.score[set+1][1])) < 10:
                            match_tiebreak = False
                            if "match tiebreak" not in p.error:
                                p.error += "\nERROR: Mix of match tiebreak scores and non-match tiebreak scores. Check all scores.\n"

                    for set in range(match.sets):
                        p_score  = "" if match.bye or t.init else match.score[set+1][i]
                        won_set = (i == match.score[0][1][set]) if set < len(match.score[0][1]) else 0 # no sets in byes/walkovers
                        p_score = "[" + p_score + "]" if t.match_tiebreak and set == 2 and p_score != "" else p_score # add square brackets for match tiebreak
                        p.text += [rd + "score" + num + "-" + str(set+1) + "=" + ("'''" + p_score + "'''" if won_set else p_score)]
                    team_no += 1
        t.qual_index += 1
        if not t.qual or t.qual_index == len(t.data[-1]):
            p.text += ["}}"]

    def MakeDraw(t, p, compact, abbr):
        if t.qual:
            p.text += ["", "=== Ergebnisse ==="]
            sections = t.SplitData(len(t.data[-1]), t.rounds)
            rounds_str = "-".join([str(len(t.data[-1]) * (2)**(c)) for c in range(t.rounds + 1)][::-1])
            t.template = "{{Turnierplan-Qualifikation-" + rounds_str + ("-Finale" if t.format == 53 else "")
            for i in range(len(sections)): # no logical section headings
                ordinal = num2words(i+1, ordinal=True).capitalize()
                t.MakeSection(p, data=sections[i], rounds=t.rounds, round_names=t.round_names[:-1], format=t.format, byes=t.byes, compact=compact, abbr=abbr)
        else:
            p.text += ["", "=== Ergebnisse ==="]
            parts = int((2**t.rounds)/t.template_size) # number of sections needed
            if parts > 1: # "Finals" section needed
                if t.doubles:
                    final_rounds = {5:2, 6:3, 7:3, 8:4}
                else:
                    final_rounds = {5:2, 6:2, 7:3, 8:4} # number of rounds to show in "Finals" section given the number of rounds in the tournament
                final_rounds = final_rounds[t.rounds]
                p.text += ["==== " + ", ".join(t.round_names[-(final_rounds+1):-1]) + " ===="]
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
                    p.text += ["==== " + half + " ===="] if half != "" and t.rounds > 5 else []
                    p.text += ["===== " + half_curr + " " + str(int(index_curr%(parts/2))+1) + " ====="]  # add section heading before each section
                    index_curr += 1
                t.MakeSection(p, data=section, rounds=section_rounds, round_names=t.round_names[:section_rounds], format=(3 if t.format > 5 else t.format), byes=t.byes, compact=compact, abbr=abbr)
        t.MakeSeeds(p, sections)

def initialize():
    global name_links
    global static_name_links
    global corrections
    global new_names
    name_links = LoadJSON("data/NamesDE.json")
    static_name_links = {**LoadJSON("data/NamesDE_m.json"), **LoadJSON("data/NamesDE_f.json")}
    corrections = GetNameCorrections()
    new_names = "<h5>New names encountered:</h5>\n<ul>"

def TournamentDrawOutputDE(data, date, format, mens, qual, compact, abbr):
    initialize()
    global new_names
    empty_names = new_names
    p = Page()
    t = Tournament(data=data, mens=mens, format=format, qual=qual, date=date)
    t.MakeDraw(p, compact=compact, abbr=abbr)
    names = "" if new_names == empty_names else f"{new_names}</ul>"
    return [names, p.error + "\n".join(p.text)]
