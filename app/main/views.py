from flask import render_template, flash
from ..models import EditableHTML, Study
from flask_login import current_user

from . import main


@main.route('/')
def index():
    studies = Study.query.all()
    is_admin = False
    if current_user:
        is_admin = current_user.is_admin()
    return render_template('main/index.html', studies=studies, is_admin=is_admin)


@main.route('/about')
def about():
    editable_html_obj = EditableHTML.get_editable_html('about')
    return render_template('main/about.html',
                           editable_html_obj=editable_html_obj)
