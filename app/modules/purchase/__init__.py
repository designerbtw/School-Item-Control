from flask import Blueprint

module = Blueprint('purchase', __name__, url_prefix ='/purchase')

from app.modules.purchase import routes