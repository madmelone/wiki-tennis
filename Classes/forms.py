from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea

class FormPlayerWorldranking(FlaskForm):
    org = SelectField('Ranking Organisation', choices=[('atp', 'ATP'), ('wta', 'WTA')])
    type = SelectField('Match Type', choices=[('singles', 'singles'), ('doubles', 'doubles')])
    language = SelectField('Wikipedia Language', choices=[('en', 'en'), ('de', 'de'), ('cs', 'cs'), ('es', 'es'),
                                                          ('fr', 'fr'), ('it', 'it'), ('ja', 'ja'), ('nl', 'nl'),
                                                          ('pl', 'pl'), ('pt', 'pt'), ('ro', 'ro'), ('ru', 'ru'),
                                                          ('sv', 'sv'), ('zh', 'zh')])
    cut = IntegerField('Ranking Cut', validators=[DataRequired()])
    date = StringField('Date', validators=[DataRequired()])
    submit = SubmitField('Request')

class FormPlayerTournamentwins(FlaskForm):
    org = SelectField('Ranking Organisation', choices=[('atp', 'ATP')])
    type = SelectField('Match Type', choices=[('singles', 'singles'), ('doubles', 'doubles')])
    player = StringField('Player-ID', validators=[DataRequired()])
    language = SelectField('Wikipedia Language', choices=[('de', 'de'), ('nl', 'nl')])
    level = SelectField('Minimum Tournament Level', choices=[(1, 'ITF Futures'), (2, 'ATP Challenger'), (3, 'ATP World Tour 250 & 500'),
                                                             (4, 'ATP World Tour 1000'), (5, 'ATP Tour Finals & Grand Slams & Olympics')])
    submit = SubmitField('Request')

class FormTournamentdraw(FlaskForm):
    language = SelectField('Wikipedia language', choices=[('en', 'en'), ('de', 'de')])
    org = SelectField('Organisation', choices=[('itf', 'ITF')])
    url = StringField('Tournament link', validators=[DataRequired()])
    gender = SelectField('Gender (dewiki)', choices=[(1, "men's"), (0, "women's")])
    format = SelectField('Match format', choices=[(3, 'best of 3'), (5, 'best of 5'), (2, 'best of 3; tiebreak deciding set'), (35, 'best of 3; best of 5 final')])
    compact = SelectField('Compact draws', choices=[(1, 'yes'), (0, 'no')])
    abbr = SelectField('Abbreviated names (e.g. R. Federer)', choices=[(1, 'yes'), (0, 'no')])
    seed_links = SelectField('Seed links (enwiki)', choices=[(1, 'yes'), (0, 'no')])
    submit = SubmitField('Request')

class FormMisc(FlaskForm):
    script = SelectField('Script', choices=[('reverse', 'Table order reverser')])
    input = StringField('Input', widget=TextArea(), validators=[DataRequired()])
    submit = SubmitField('Request')
