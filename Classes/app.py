from flask import Flask, render_template, request, redirect, url_for
from Settings import Config
from datetime import datetime
import traceback

from AppPlayerTourneywins import TournamentWinsOutput, GetTournamentWins
from AppPlayerWorldranking import GetWorldRanking, RankingOutput
from AppTourneydrawEN import TournamentDrawOutputEN
from AppTourneydrawDE import TournamentDrawOutputDE
from ScrapeTournamentATP import ScrapeTournamentATP
from ScrapeTournamentITF import ScrapeTournamentITF
from AppMisc import GetMisc
from forms import *

#Initiate Flask with config
app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def home():
    return render_template('about.html')

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/playerworldranking/', methods=['GET', 'POST'])
def playerworldranking():
    form = FormPlayerWorldranking()
    if request.method == 'POST':
        org = request.form.get('org')
        type = request.form.get('type')
        cut = request.form.get('cut')
        language = request.form.get('language')
        date = request.form.get('date')
        return redirect(url_for('outputranking', org=org, type=type, cut=cut, language=language, date=date))
    return render_template('playerworldranking.html', form=form)

@app.route('/playerwins/', methods=['GET', 'POST'])
def playerwins():
    form = FormPlayerTournamentwins()
    if request.method == 'POST':
        org = request.form.get('org')
        type = request.form.get('type')
        player = request.form.get('player')
        language = request.form.get('language')
        level = request.form.get('level')
        return redirect(url_for('outputplayerwins', org=org, type=type, player=player, language=language, level=level))
    return render_template('playerwins.html', form=form)

@app.route('/tourneydraw/', methods=['GET', 'POST'])
def tourneydraw():
    form = FormTournamentdraw()
    if request.method == 'POST':
        language = request.form.get('language')
        org = request.form.get('org')
        url = request.form.get('url')
        gender = request.form.get('gender')
        format = request.form.get('format')
        compact = request.form.get('compact')
        abbr = request.form.get('abbr')
        seed_links = request.form.get('seed_links')
        return redirect(url_for('outputtourneydraw', language=language, org=org, url=url, gender=gender, format=format, compact=compact, abbr=abbr, seed_links=seed_links))
    return render_template('tourneydraw.html', form=form)

@app.route('/misc/', methods=['GET', 'POST'])
def misc():
    form = FormMisc()
    if request.method == 'POST':
        script = request.form.get('script')
        input = request.form.get('input')
        output = GetMisc(script=script, input=input)
        return render_template('outputmisc.html', result=output)
    return render_template('misc.html', form=form)

@app.route('/outputranking/', methods=['GET', 'POST'])
def outputranking():
    #Get variables from form
    org = request.args.get('org', type = str)
    type = request.args.get('type', type = str)
    cut = request.args.get('cut', default='100', type = int)
    language = request.args.get('language', type = str)
    date = request.args.get('date', type = str)
    #Run GetWorldRanking()
    ranking = GetWorldRanking(org, type, cut, language, date)
    result = RankingOutput(ranking, org, type, cut, language, date)
    return render_template('outputranking.html', result=result)

@app.route('/outputplayerwins/', methods=['GET', 'POST'])
def outputplayerwins():
    #Get variables from form
    org = request.args.get('org', type = str)
    type = request.args.get('type', type = str)
    player = request.args.get('player', type = str)
    language = request.args.get('language', type = str)
    level = request.args.get('level', type = int)
    #Run GetTournamentWins()
    wins = GetTournamentWins(org, player, type, level)
    result = TournamentWinsOutput(wins, language, type)
    return render_template('outputplayerwins.html', result=result)

@app.route('/outputtourneydraw/', methods=['GET', 'POST'])
def outputtourneydraw():
    #Get variables from form
    language = request.args.get('language', type = str)
    org = request.args.get('org', type = str)
    url = request.args.get('url', type = str)
    gender = request.args.get('gender', type = int)
    format = request.args.get('format', type = int)
    compact = request.args.get('compact', type = int)
    abbr = request.args.get('abbr', type = int)
    seed_links = request.args.get('seed_links', type = int)
    errors = ""
    error = False
    message = ""
    names = []
    # Rudimentary input validation
    itfurl = "https://event.itftennis.com/itf/web/usercontrols/tournaments/tournamentprintabledrawsheets.aspx?"
    atpurl = "https://www.atptour.com/en/scores/"
    atpurl2 = "https://www.atptour.com/scores/archive/"
    if org == 'itf' and not url.startswith(itfurl):
        error = True
        output = "Invalid URL: should be a printable draw in format: " + itfurl + "...."
    elif org != 'itf' and not (url.startswith(atpurl) or url.startswith(atpurl2)):
        error = True
        output = "Invalid URL: should be a printable draw in format: " + atpurl + "...."
    else:
        try:
            # Scrape data, then create draw
            if org == "itf":
                data, qual, doubles, date = ScrapeTournamentITF(url=url)
            else:
                data, format2, qual, doubles, date, errors = ScrapeTournamentATP(url=url, data=None)
                format = format if format2 == None else format2
            if language == "en":
                names, output = TournamentDrawOutputEN(data=data, date=date, format=format, qual=qual, compact=compact, abbr=abbr, seed_links=seed_links)
            elif language == "de":
                names, output = TournamentDrawOutputDE(data=data, date=date, format=format, mens=gender, qual=qual, compact=compact, abbr=abbr)
        except Exception:
            message = str(traceback.format_exc())
            error = True
            names = ""
            output = 'The program has encountered an error. Please go back and check that all inputs are correct. If the error persists, <s>please contact <a href="https://en.wikipedia.org/wiki/User_talk:Somnifuguist">Somnifuguist</a></s> see if you can find the same draw on the other site.'
        output = errors + output
        timestamp = "[" + str(datetime.now())[:-7] + "] "
        log = timestamp + ("PASS: " if not error else "FAIL: ") + "lang=" + language + ", format=" + str(format) + ", compact=" + str(compact) + ", abbr=" + str(abbr) + ", seed_links=" + str(seed_links) +", url=" + url + (", message=\n" + message if message != "" else "")  + '\n'
        with open('tourneydraw.log','a') as f:
            f.write(log)
    return render_template('outputtourneydraw' + ('error' if error else '') + '.html', result=output, names=names)

if __name__ == '__main__':
    app.run(debug=True)
