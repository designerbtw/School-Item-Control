from flask import render_template
from flask_login import login_required

from . import module


# Create a main page
@module.route('/')
@login_required
def main():
    return render_template('main/main.html', title='Управление спортивным инвентарем')