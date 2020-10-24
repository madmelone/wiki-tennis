from flask import Flask, render_template, request, redirect, url_for
from Settings import Config

from AppPlayerTourneywins import TournamentWinsOutput, GetTournamentWins
from AppPlayerWorldranking import GetWorldRanking, RankingOutput
from AppTourneydrawEN import TournamentDrawOutputEN
from AppTourneydrawDE import TournamentDrawOutputDE
from ScrapeTournamentITF import ScrapeTournamentITF
from forms import FormPlayerWorldranking, FormPlayerTournamentwins, FormTournamentdraw

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
        year = request.form.get('year')
        doubles = request.form.get('doubles')
        format = request.form.get('format')
        qual = request.form.get('qual')
        compact = request.form.get('compact')
        abbr = request.form.get('abbr')
        seed_links = request.form.get('seed_links')
        return redirect(url_for('outputtourneydraw', language=language, org=org, url=url, year=year, doubles=doubles, format=format, qual=qual, compact=compact, abbr=abbr, seed_links=seed_links))
    return render_template('tourneydraw.html', form=form)

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
    year = request.args.get('year', type = int)
    doubles = request.args.get('doubles', type = int)
    format = request.args.get('format', type = int)
    qual = request.args.get('qual', type = int)
    compact = request.args.get('compact', type = int)
    abbr = request.args.get('abbr', type = int)
    seed_links = request.args.get('seed_links', type = int)
    if "https://event.itftennis.com/itf/web/usercontrols/tournaments/tournamentprintabledrawsheets.aspx?" in url:
        # Scrape data, then create draw
        data = ScrapeTournamentITF(url=url, qual=qual, doubles=doubles)
        if language == "en":
            draw = TournamentDrawOutputEN(data=data, year=year, format=format, qual=qual, compact=compact, abbr=abbr, seed_links=seed_links)
        elif language == "de":
            draw = TournamentDrawOutputDE(data=data, year=year, format=format, qual=qual, compact=compact, abbr=abbr)
    else: # extremely basic input validation
        draw = "Invalid URL, should be a printable draw in format: https://event.itftennis.com/itf/web/usercontrols/tournaments/tournamentprintabledrawsheets.aspx?"
    return render_template('outputtourneydraw.html', result=draw)

if __name__ == '__main__':
    app.run(debug=True)
