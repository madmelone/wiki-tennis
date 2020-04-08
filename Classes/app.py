from flask import Flask, render_template, request

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/about/')
def about():
    page = request.args.get('page', default = 1, type = int)
    filter = request.args.get('filter', default = '*', type = str)
    return render_template('about.html')
if __name__ == '__main__':
    app.run(debug=True)