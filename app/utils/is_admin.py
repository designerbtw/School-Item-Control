from functools import wraps

from flask_login import current_user

from flask import flash, redirect, url_for


# Check API token in request headers
def is_admin(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.role.name == "admin":
            return func(*args, **kwargs)
        flash("У вас нет необходимых прав!", "warning")
        return redirect(url_for('main.main'))

    return decorated_function