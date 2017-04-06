import json
from flask import render_template

from . import request_blueprint

from ..models import Variable, Study
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
