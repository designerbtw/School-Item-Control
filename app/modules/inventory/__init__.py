from flask import Blueprint

module = Blueprint('inventory', __name__, url_prefix ='/inventory')

from app.modules.inventory import routes