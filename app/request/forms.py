from flask_wtf import Form
from wtforms.fields import StringField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length
"""
RequestItem = namedtuple('RequestItem', ['item_id', 'want', 'name'])


class RequestItemForm(Form):
    item_id = HiddenField()
    want = BooleanField()


class RequestListForm(Form):
    def __init__(self, *args, **kwargs):
        super(RequestListForm, self).__init__(*args, **kwargs)

        # just a little trickery to get custom labels
        # on the list's checkboxes
        for item_form in self.items:
            for item in kwargs['data']['items']:
                if item.item_id == item_form.item_id.data:
                    item_form.want.label = ''
                    item_form.label = item.name

    items = FieldList(FormField(RequestItemForm))

"""


class NewFieldForm(Form):
    field_name = StringField(
            'Field Name', validators=[InputRequired(), Length(1, 128)])
    mandatory = BooleanField('Mandatory', validators=[InputRequired()])
    submit = SubmitField('Add new field')
