from flask import Blueprint

request_blueprint = Blueprint('request', __name__)

from . import views  # noqa
