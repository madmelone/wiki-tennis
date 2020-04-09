from flask import Flask, render_template, request, redirect, url_for
from forms import *
import sys
from Settings import Config
from AppPlayerWorldranking import *

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

@app.route('/playerwins/')
def playerwins():
    #org = request.args.get('org', default = 1, type = str)
    #type = request.args.get('type', default = '*', type = str)
    #playerid = request.args.get('playerid', default = '*', type = str)
    #language = request.args.get('language', default = '*', type = str)
    return render_template('playerwins.html')

@app.route('/tourneydraw/')
def tourneydraw():
    #org = request.args.get('org', default = 1, type = str)
    #type = request.args.get('type', default = '*', type = str)
    #year = request.args.get('cut', default = '*', type = str)
    #language = request.args.get('language', default = '*', type = str)
    return render_template('tourneydraw.html')

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

if __name__ == '__main__':
    app.run(debug=True)