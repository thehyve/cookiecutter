from flask_wtf import Form
from wtforms import ValidationError
from wtforms.fields import StringField, SubmitField
from wtforms.validators import InputRequired, Length


class ChangeTransmartUrl(Form):
    url = StringField(
        'New URL', validators=[InputRequired(), Length(1, 128)])
    submit = SubmitField('Update url')


class ChangeTransmartVersion(Form):
    version = StringField(
        'New Version', validators=[InputRequired(), Length(1, 128)])
    submit = SubmitField('Update version')
