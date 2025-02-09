from flask import Blueprint

module = Blueprint('request', __name__, url_prefix ='/request')

from app.modules.request import routes