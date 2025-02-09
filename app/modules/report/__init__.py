from flask import Blueprint

module = Blueprint('report', __name__, url_prefix ='/report')

from app.modules.report import routes