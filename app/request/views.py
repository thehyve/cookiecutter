import json
import datetime
from flask import render_template, abort, redirect, url_for
from flask_login import current_user

from . import request_blueprint

from .forms import NewFieldForm, StageForm, FinalApprovalForm

from ..models import (Variable, Study, Request,
                      RequestProcess, RequestField,
                      RequestVariable, RequestFieldAnswer, ProcessStep)
from ..decorators import admin_required
from ..concept_tree import build_tree, TreeEncoder

from flask_login import login_required
from .. import db
from .utils import (get_approval_form, get_form,
                    parse_request_vars, create_default_process)


@request_blueprint.route('/new/<study_name>', methods=['GET', 'POST'])
@login_required
def new_request(study_name):
    study = Study.query.filter(Study.name == study_name).first()
    variables = Variable.query.filter(Variable.study_id == study.id).all()
    concept_tree = build_tree(variables)
    concept_tree = json.dumps(concept_tree, cls=TreeEncoder)
    approval_process = RequestProcess.query.filter(RequestProcess.version == 1).first()
    if not approval_process:
        approval_process = create_default_process()
    fields = RequestField.query.filter(RequestField.process_id == approval_process.id).all()
    form = get_form(fields)
    if form.validate_on_submit():
        new_request = Request()
        new_request.user_id = current_user.id
        new_request.study_id = study.id
        new_request.issued_time = datetime.datetime.now().strftime("%Y-%m-%d")
        new_request.status = "New"
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
            answer.field_id = field.id
            answer.request_id = new_request.id
            db.session.add(answer)
        db.session.commit()
        return redirect(url_for('request.my_requests'))

    return render_template('request/request.html',
                           concept_tree=concept_tree, study_name=study_name, form=form)


@request_blueprint.route('/<request_id>', methods=['GET', 'POST'])
@login_required
def request_view(request_id):
    req = Request.query.filter(Request.id == request_id).first()
    is_admin = current_user.is_admin()
    if not current_user.id == req.user_id and not is_admin:
        abort(403)
    variables = Variable.query.filter(Variable.study_id == req.study.id).all()
    selected_vars = RequestVariable.query.filter(RequestVariable.request_id == req.id).all()
    selected_vars = [v.variable_id for v in selected_vars]
    concept_tree = build_tree(variables, selected_vars, disabled=not is_admin)
    concept_tree = json.dumps(concept_tree, cls=TreeEncoder)
    answers = RequestFieldAnswer.query.filter(RequestFieldAnswer.request_id == req.id).all()
    stages = ProcessStep.query.filter(ProcessStep.request_process_id == 1).all()
    approval_form = get_approval_form(stages)
    if approval_form.validate_on_submit() and is_admin:
        stage_id = int(approval_form.stage.data)
        stage = ProcessStep.query.filter(ProcessStep.id == stage_id).first()
        if stage.approves:
            return redirect(url_for('request.approve', requestid=request_id))
        else:
            req.status = stage.name
            db.session.commit()
    return render_template('request/request.html',
                           concept_tree=concept_tree, study_name=req.study.name,
                           selected_vars=selected_vars, form=approval_form, answers=answers,
                           is_admin=is_admin, current_stage=req.status, read_only=not is_admin)


@request_blueprint.route('/', methods=['GET', 'POST'])
@login_required
def my_requests():
    requests = Request.query.all()

    return render_template('request/myrequests.html', requests=requests)


@request_blueprint.route('/configure-fields', methods=['GET', 'POST'])
@login_required
def configure_request():
    form = NewFieldForm()
    approval_process = RequestProcess.query.filter(RequestProcess.version == 1).first()
    if not approval_process:
        approval_process = create_default_process()
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


@request_blueprint.route('/configure-stages', methods=['GET', 'POST'])
@login_required
def configure_stages():
    stage_form = StageForm()
    approval_process = RequestProcess.query.filter(RequestProcess.version == 1).first()
    if not approval_process:
        approval_process = create_default_process()
    if stage_form.validate_on_submit():
        new_stage = ProcessStep()
        new_stage.request_process_id = approval_process.id
        new_stage.name = stage_form.stage_name.data
        new_stage.description = stage_form.description.data
        new_stage.approves = stage_form.approval.data
        new_stage.denies = stage_form.denial.data
        db.session.add(new_stage)
        db.session.commit()
    stages = ProcessStep.query.filter(ProcessStep.request_process_id == approval_process.id).all()
    return render_template('request/configure_stages.html', stages=stages,
                           stage_form=stage_form)


@request_blueprint.route('/approve/<requestid>', methods=['GET', 'POST'])
@login_required
@admin_required
def approve(requestid):
    form = FinalApprovalForm()
    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data
        approve_request(requestid, username, pwd)
        return redirect(url_for('request.request_view', requestid))
    return render_template('request/approve.html', form=form)
