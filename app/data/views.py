import os
from tempfile import NamedTemporaryFile
from flask import abort, flash, redirect, render_template, send_file, url_for, request
from flask_login import current_user, login_required

from .forms import (ChangeTransmartUrl, ChangeTransmartVersion,
                    SyncForm, CodebookUploadForm, AttachmentUploadForm)
from . import data
from .. import db
from ..decorators import admin_required
from flask import current_app as app
from ..models import Role, User, Request, Attachment
from ..tm_extractor import sync
from ..codebooks import validate_codebook, apply_codebook, generate_codebook_template
from ..models import Study
from ..attachments import register_request_attachment, register_study_attachment, get_attachment


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


@data.route('/request-data/<requestid>', methods=['GET', 'POST'])
@login_required
def data_view(requestid):
    req = Request.query.filter(Request.id == requestid).first()
    if not req:
        abort(404)
    if not req.user_id == current_user.id and not current_user.is_admin():
        abort(403)
    form = AttachmentUploadForm()
    if form.validate_on_submit():
        uploaded = form.codebook.data
        register_request_attachment(uploaded.read(), uploaded.filename, current_user, req) # TODO: for bigger files thats not sustainable
    attachments = Attachment.query.filter(Attachment.request_id == req.id).all()
    return render_template('data/attachment_management.html', attachments=attachments, form=form)

@data.route('/remove/<attachmentid>')
@login_required
def remove(attachmentid):
    attachment = Attachment.query.filter(Attachment.id == attachmentid).first()
    if not attachment:
        abort(404)
    if not current_user.id == attachment.owner and not current_user.is_admin():
        abort(403)
    file_path = get_attachment(attachment)
    os.unlink(file_path)
    db.session.delete(attachment)
    db.session.commit()
    return redirect(request.referrer)


@data.route('/download/<attachmentid>')
@login_required
def download(attachmentid):
    attachment = Attachment.query.filter(Attachment.id == attachmentid).first()
    if not attachment:
        abort(404)
    if not attachment.owner == current_user.id and not current_user.is_admin():
        abort(403)
    attachment_file = get_attachment(attachment)
    return send_file(attachment_file, as_attachment=True, attachment_filename=attachment.name)

@data.route('/study-data/<studyid>',  methods=['GET', 'POST'])
@login_required
@admin_required
def study_data_view(studyid):
    study = Study.query.filter(Study.id== studyid).first()
    if not study:
        abort(404)
    form = AttachmentUploadForm()
    if form.validate_on_submit():
        uploaded = form.codebook.data
        register_study_attachment(uploaded.read(), uploaded.filename, current_user, study) # TODO: for bigger files thats not sustainable
    attachments = Attachment.query.filter(Attachment.study_id == studyid).all()
    return render_template('data/attachment_management.html', attachments=attachments, form=form)


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
