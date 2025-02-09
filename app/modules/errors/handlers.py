from flask import render_template, request, make_response, redirect, url_for
from app import db, logger
from . import module

from app.api.errors import error_response as api_error_response

def wants_json_response():
    return request.accept_mimetypes['application/json'] >= \
        request.accept_mimetypes['text/html']

@module.app_errorhandler(404)
def not_found_error(error):
    if wants_json_response():
        return api_error_response(404)
        pass
    return render_template('errors/404.html'), 404

@module.app_errorhandler(401)
def unauthorized(error):
    return make_response(redirect(url_for('register.login')))

@module.app_errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}")
    db.session.rollback()
    if wants_json_response():
        return api_error_response(500)
        pass
    return render_template('errors/500.html'), 500