from flask import render_template
from ..models import EditableHTML, Study

from . import main


@main.route('/')
def index():
    studies = Study.query.all()
    return render_template('main/index.html', studies=studies)


@main.route('/about')
def about():
    editable_html_obj = EditableHTML.get_editable_html('about')
    return render_template('main/about.html',
                           editable_html_obj=editable_html_obj)
