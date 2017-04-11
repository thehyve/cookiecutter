import json
from flask import render_template

from . import request_blueprint

from ..models import (Variable, Study, Request,
                      RequestProcess, RequestField)
from ..concept_tree import build_tree, TreeEncoder

from flask_login import login_required


@request_blueprint.route('/<study_name>', methods=['GET', 'POST'])
@login_required
def request_view(study_name):
    study = Study.query.filter(Study.name == study_name).first()
    variables = Variable.query.filter(Variable.study_id == study.id).all()
    concept_tree = build_tree(variables)
    concept_tree = json.dumps(concept_tree, cls=TreeEncoder)
    return render_template('request/request.html',
                           concept_tree=concept_tree, study_name=study_name)


@request_blueprint.route('/', methods=['GET', 'POST'])
@login_required
def my_requests():
    requests = Request.query.all()
    return render_template('request/myrequests.html', requests=requests)


@request_blueprint.route('/configure', methods=['GET', 'POST'])
@login_required
def configure_request():
    approval_process = RequestProcess.query.filter(RequestProcess.version == 1).first()
    fields = RequestField.query \
        .filter(RequestField.process_id == approval_process.id).all()
    return render_template('request/configure_request.html', fields=fields)
