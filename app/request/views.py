import json
from flask import render_template

from . import request_blueprint
from flask_wtf import Form
from wtforms.fields import StringField, SubmitField, BooleanField, HiddenField
from wtforms.validators import InputRequired, Length
from .forms import NewFieldForm

from ..models import (Variable, Study, Request,
                      RequestProcess, RequestField,
                      RequestVariable, RequestFieldAnswer)
from ..concept_tree import build_tree, TreeEncoder

from flask_login import login_required
from .. import db


@request_blueprint.route('/<study_name>', methods=['GET', 'POST'])
@login_required
def request_view(study_name):
    study = Study.query.filter(Study.name == study_name).first()
    variables = Variable.query.filter(Variable.study_id == study.id).all()
    concept_tree = build_tree(variables)
    concept_tree = json.dumps(concept_tree, cls=TreeEncoder)
    approval_process = RequestProcess.query.filter(RequestProcess.version == 1).first()
    if not approval_process:
        approval_process = RequestProcess()
        RequestProcess.version = 1
        db.session.add(approval_process)
        db.session.commit()
    fields = RequestField.query.filter(RequestField.process_id == approval_process.id).all()
    form = get_form(fields)
    if form.validate_on_submit():
        new_request = Request()
        db.session.add(new_request)
        db.session.commit()
        request_vars = parse_request_vars(form.request_vars.data)
        for var in request_vars:
            req_var = RequestVariable()
            req_var.request_id = new_request.id
            req_var.variable_id = var
            db.session.add(req_var)
        for field in fields:
            answer = RequestFieldAnswer()
            answer.answer = getattr(form, field.name).data
            answer.request_field_id = field.id
            answer.request_id = new_request.id
            db.session.add(answer)
        db.session.commit()

    return render_template('request/request.html',
                           concept_tree=concept_tree, study_name=study_name, form=form)


@request_blueprint.route('/', methods=['GET', 'POST'])
@login_required
def my_requests():
    requests = Request.query.all()
    return render_template('request/myrequests.html', requests=requests)


@request_blueprint.route('/configure', methods=['GET', 'POST'])
@login_required
def configure_request():
    form = NewFieldForm()
    approval_process = RequestProcess.query.filter(RequestProcess.version == 1).first()
    if not approval_process:
        approval_process = RequestProcess()
        RequestProcess.version = 1
        db.session.add(approval_process)
        db.session.commit()
    if form.validate_on_submit():
        field_name = form.field_name.data
        is_mandatory = form.mandatory.data
        new_field = RequestField()
        new_field.mandatory = is_mandatory
        new_field.name = field_name
        new_field.process_id = approval_process.id
        db.session.add(new_field)
        db.session.commit()
    fields = RequestField.query \
        .filter(RequestField.process_id == approval_process.id).all()
    return render_template('request/configure_request.html', fields=fields, form=form)


def get_form(fields):
    """Create a wtf-form class out of process fields"""
    class_body = {'submit': SubmitField('Submit Request'),
                  'request_vars': HiddenField("request_vars")}
    for field in fields:
        class_body[field.name] = StringField()
    DynamicForm = type('DynamicForm', (Form,), class_body)
    form = DynamicForm()
    return form


def parse_request_vars(request_vars):
    return request_vars.split(',')
