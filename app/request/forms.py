from flask_wtf import Form
from wtforms.fields import StringField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length


class NewFieldForm(Form):
    field_name = StringField(
        'Field Name', validators=[InputRequired(), Length(1, 128)])
    mandatory = BooleanField('Mandatory', default=False)
    submit = SubmitField('Add new field')


class StageForm(Form):
    stage_name = StringField(
        'Stage Name', validators=[InputRequired(), Length(1, 128)])
    description = StringField(
        'Description', validators=[InputRequired(), Length(1, 1024)])
    approval = BooleanField('Approval Stage', default=False)
    denial = BooleanField('Dismissal Stage', default=False)
    submit = SubmitField('Add new stage')
