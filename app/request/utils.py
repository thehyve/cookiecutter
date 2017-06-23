from flask_wtf import Form
from wtforms.fields import StringField, SubmitField, HiddenField, SelectField

from app.models import RequestProcess, RequestVariable, User, Attachment
from .. import db
from app.tm_extractor import get_observations, observations_to_tsv
from ..attachments import deposit_dataset, get_attachment, register_request_attachment


def get_form(fields):
    """Create a wtf-form class out of process fields"""
    class_body = {'submit': SubmitField('Submit Request'),
                  'request_vars': HiddenField("request_vars")}
    for field in fields:
        class_body[field.name] = StringField()
    DynamicForm = type('DynamicForm', (Form,), class_body)
    form = DynamicForm()
    return form


def get_approval_form(stages):
    choices = [(str(stage.id), stage.name) for stage in stages]
    class_body = {'submit': SubmitField('Submit'), 'stage': SelectField('Change Request Stage', choices=choices)}
    DynamicForm = type('DynamicForm', (Form,), class_body)
    form = DynamicForm()
    return form


def parse_request_vars(request_vars):
    return request_vars.split(',')


def create_default_process():
    approval_process = RequestProcess()
    RequestProcess.version = 1
    db.session.add(approval_process)
    db.session.commit()
    return approval_process


def approve_request(request, token, tm_url):
    user = User.query.filter(User.id == request.user_id).first()
    _vars = RequestVariable.query.filter(RequestVariable.request_id == request.id).all()
    concepts = [var.variable.path for var in _vars]
    observations = get_observations(token, tm_url, request.study.name, concepts)
    tsv = observations_to_tsv(observations)
    attach_study_attachments(request)
    return deposit_dataset(tsv, user, request)


def attach_study_attachments(request):
    study_attachments = Attachment.query.filter(Attachment.study_id == request.study_id).all()
    for att in study_attachments:
        att_path = get_attachment(att)
        with open(att_path, 'rb') as outfile:
            content = outfile.read()
            register_request_attachment(content, att.name, request.user, request, True)
