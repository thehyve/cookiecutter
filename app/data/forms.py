from flask_wtf import Form
from wtforms import ValidationError
from wtforms.fields import StringField, SubmitField, PasswordField
from wtforms.validators import InputRequired, Length


class ChangeTransmartUrl(Form):
    url = StringField(
        'New URL', validators=[InputRequired(), Length(1, 128)])
    submit = SubmitField('Update url')


class ChangeTransmartVersion(Form):
    version = StringField(
        'New Version', validators=[InputRequired(), Length(1, 128)])
    submit = SubmitField('Update version')


class SyncForm(Form):
    username = StringField('Transmart username', validators=[InputRequired()])
    password = PasswordField('Transmart password', validators=[InputRequired()])
    submit = SubmitField('Sync now (this operation will take a long time!)')
