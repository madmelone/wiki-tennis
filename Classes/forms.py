from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired


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