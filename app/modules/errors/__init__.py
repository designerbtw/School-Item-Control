from flask import Blueprint

module = Blueprint('errors', __name__)

from app.modules.errors import handlers