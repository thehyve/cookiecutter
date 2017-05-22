from flask_wtf import Form
from wtforms.fields import StringField, SubmitField, HiddenField, SelectField

from app.models import RequestProcess, ProcessStep, RequestVariable
from .. import db
from app.tm_extractor import get_observations


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
    choices = [(stage.id, stage.name) for stage in stages]
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


def change_status(stage_id, request):
    stage = ProcessStep.query.filter(ProcessStep.id == stage_id).first()
    request.status = stage.name
    return stage


def approve_request(requestid, token, tm_url):
    vars = RequestVariable.query.filter(RequestVariable.request_id == requestid).all()
    concepts = [var.variable.path for var in vars]
    observations = get_observations(token, tm_url, concepts)
    return make_dataset(observations, requestid)
