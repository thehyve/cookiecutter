from flask import abort, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required
from flask_rq import get_queue

from .forms import (ChangeTransmartUrl, ChangeTransmartVersion)
from . import admin
from .. import db
from ..decorators import admin_required
from ..models import Role, User
from ..tm_extractor import sync


@admin.route('/configure-transmart', methods=['GET', 'POST'])
@login_required
@admin_required
def configure_transmart():
    return render_template('admin/configure_transmart.html')


@admin.route('/sync', methods=['GET', 'POST'])
@login_required
@admin_required
def sync_data():
    
    sync(username, password, tm_url)
    return 'ok', 200