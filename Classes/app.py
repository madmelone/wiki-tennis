from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('PlayerWorldranking.html')

@app.route('/about/')
def about():
    return render_template('AppAbout.html')

@app.route('/PlayerWorldranking/')
def about():
    #org = request.args.get('org', default = 1, type = str)
    #type = request.args.get('type', default = '*', type = str)
    #cut = request.args.get('cut', default = '*', type = int)
    #language = request.args.get('language', default = '*', type = str)
    #date = request.args.get('date', default = '*', type = str)
    return render_template('PlayerWorldranking.html')

@app.route('/TournamentDraw/')
def about():
    #org = request.args.get('org', default = 1, type = str)
    #type = request.args.get('type', default = '*', type = str)
    #year = request.args.get('cut', default = '*', type = str)
    #language = request.args.get('language', default = '*', type = str)
    return render_template('TournamentDraw.html')

@app.route('/PlayerTourneywins/')
def about():
    #org = request.args.get('org', default = 1, type = str)
    #type = request.args.get('type', default = '*', type = str)
    #playerid = request.args.get('playerid', default = '*', type = str)
    #language = request.args.get('language', default = '*', type = str)
    return render_template('PlayerTourneywins.html')

if __name__ == '__main__':
    app.run(debug=True)