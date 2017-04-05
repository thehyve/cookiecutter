from flask import abort, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required

from .forms import RequestItemForm, RequestListForm, RequestItem
from . import request_blueprint

from ..models import Variable
from ..concept_tree import build_tree

from flask_login import (current_user, login_required, login_user,
                         logout_user)


@request_blueprint.route('/<int:study_name>', methods=['GET', 'POST'])
@login_required
def request_view(study_name):
    study = Study.query.filter(Study.name == study_name).first()
    variables = Variable.query.filter(Variable.study_id == study.id).all()
    build_tree()
    return render_template('data/configure_transmart.html', form=form)



