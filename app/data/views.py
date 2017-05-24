from tempfile import NamedTemporaryFile
from flask import abort, flash, redirect, render_template, send_file
from flask_login import current_user, login_required

from .forms import (ChangeTransmartUrl, ChangeTransmartVersion,
                    SyncForm, CodebookUploadForm)
from . import data
from .. import db
from ..decorators import admin_required
from flask import current_app as app
from ..models import Role, User, Request, Attachment
from ..tm_extractor import sync
from ..codebooks import validate_codebook, apply_codebook, generate_codebook_template
from ..models import Study


@data.route('/configure-transmart', methods=['GET', 'POST'])
@login_required
@admin_required
def configure_transmart():
    tm_url = app.config['TRANSMART_URL']
    tm_version = app.config['TRANSMART_VERSION']
    return render_template('data/configure_transmart.html', tm_url=tm_url,
                           tm_version=tm_version)


@data.route('/change-version', methods=['GET', 'POST'])
@login_required
@admin_required
def change_version():
    form = ChangeTransmartVersion()
    tm_url = app.config['TRANSMART_URL']
    tm_version = app.config['TRANSMART_VERSION']
    if form.validate_on_submit():
        app.config['TRANSMART_VERSION'] = form.version.data
        flash('Transmart URL changed', 'form-success')
    return render_template('data/configure_transmart.html', tm_url=tm_url,
                           tm_version=tm_version, form=form)


@data.route('/change-url', methods=['GET', 'POST'])
@login_required
@admin_required
def change_url():
    form = ChangeTransmartUrl()
    tm_url = app.config['TRANSMART_URL']
    tm_version = app.config['TRANSMART_VERSION']
    if form.validate_on_submit():
        app.config['TRANSMART_URL'] = form.url.data
        flash('Transmart URL changed', 'form-success')
    return render_template('data/configure_transmart.html', tm_url=tm_url,
                           tm_version=tm_version, form=form)


@data.route('/sync', methods=['GET', 'POST'])
@login_required
@admin_required
def sync_view():
    form = SyncForm()
    tm_url = app.config['TRANSMART_URL']
    tm_version = app.config['TRANSMART_VERSION']
    if form.validate_on_submit():
        password = form.password.data
        username = form.username.data
        sync(username, password, tm_url)
    return render_template('data/configure_transmart.html', tm_url=tm_url,
                           tm_version=tm_version, form=form)


@data.route('/request-data/<requestid:int>')
@login_required
def data_view(requestid):
    req = Request.query.filter(Request.id == requestid).first()
    if not req:
        abort(404)
    if not req.user_id == current_user.id and not current_user.is_admin():
        abort(403)
    attachments = Attachment.query.filter(Attachment.request_id == req.id).all()
    return render_template('data/request_data.html', attachments=attachments)


@data.route('/codebook/<study_name>', methods=['GET', 'POST'])
@login_required
def codebook_upload(study_name):
    form = CodebookUploadForm()
    study = Study.query.filter(Study.name == study_name).first()
    if not study:
        abort(404)
    validation_errors = []
    report = {}
    if form.validate_on_submit():
        tmp = NamedTemporaryFile(delete=False)
        form.codebook.data.save(tmp)
        tmp.close()
        validation_errors = validate_codebook(tmp.name)
        if not validation_errors:
            report = apply_codebook(study, tmp.name)
    return render_template('data/codebook.html', form=form,
                           validation_errors=validation_errors,
                           study=study, report=report)


@data.route('/codebook-template/<studyname>', methods=['GET'])
@login_required
def codebook_generate(studyname):
    study = Study.query.filter(Study.name == studyname).first()
    if not study:
        abort(404)
    codebook_template = generate_codebook_template(study)
    file_name = "{0}_codebook_template.txt".format(studyname)
    return send_file(codebook_template, as_attachment=True, attachment_filename=file_name)
