from flask import abort, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required

from .forms import (ChangeTransmartUrl, ChangeTransmartVersion, SyncForm)
from . import data
from .. import db
from ..decorators import admin_required
from flask import current_app as app
from ..models import Role, User
from ..tm_extractor import sync


@data.route('/configure-transmart', methods=['GET', 'POST'])
@login_required
@admin_required
def configure_transmart():
    print(app.config)
    tm_url = app.config['TRANSMART_URL']
    tm_version = app.config['TRANSMART_VERSION']
    return render_template('data/configure_transmart.html',  tm_url=tm_url,
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
        print(app.config)
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
                           tm_version=tm_version,  form=form)
