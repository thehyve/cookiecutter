from collections import namedtuple
from wtforms import Form, FieldList, BooleanField, HiddenField, FormField
from webob.multidict import MultiDict

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
                    item_form.want.label =''
                    item_form.label = item.name

    items = FieldList(FormField(RequestItemForm))
