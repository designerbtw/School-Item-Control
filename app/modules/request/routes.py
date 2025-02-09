from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.models import Request, RequestType
from app import db, logger
from app.utils.is_admin import is_admin
from . import module, forms


# show all requests
@module.route('/')
@login_required
def requests():
    user_requests = []
    if current_user.role.name == 'admin':
        user_requests = Request.query.all()
        user_requests = user_requests[::-1]
    if current_user.role.name == 'user':
        user_requests = Request.query.filter_by(user_id=current_user.id).all()
    return render_template('request/requests.html', title='Заявки', user_requests=user_requests)


# creating new request
@module.route('/create/<string:type>/<int:user_id>/<int:item_id>', methods=['POST', "GET"])
@login_required
def create_request(type, user_id, item_id):
    logger.debug(f"Processing new request for Item: {item_id}")
    try:
        if type == 'repair':
            type = RequestType.REPAIR
            Request.create_request(user_id=user_id,
                                   item_id=item_id,
                                   type=type,
                                   quantity=0)
            logger.debug(f"Request REPAIR successfully added.")
        elif type == 'change':
            type = RequestType.CHANGE
            Request.create_request(user_id=user_id,
                                   item_id=item_id,
                                   type=type,
                                   quantity=0)
            logger.debug(f"Request CHANGE successfully added.")
        elif type == 'take':
            form = forms.CreateRequestForm()
            type = RequestType.TAKE
            if form.validate_on_submit():
                Request.create_request(user_id=user_id,
                                       item_id=item_id,
                                       type=type,
                                       quantity=form.quantity.data)
                logger.debug(f"Request TAKE successfully added.")
    except ValueError:
        db.session.rollback()
        flash("Некорректная заявка!", 'warning')
        return redirect(url_for('inventory.my_inventory'))
    except Exception as e:
        logger.error(f"Error adding Item {item_id}: {e}")
        db.session.rollback()
    return redirect(url_for('request.requests'))

# approve request
@module.route('/approve/<int:id>')
@login_required
@is_admin
def approve_request(id):
    try:
        request: Request = Request.query.filter_by(id=id).first()
        request.approve_request()
        logger.debug(f"Successfully approve request {request.id}")
        return redirect(url_for('request.requests'))
    except ValueError:
        db.session.rollback()
        flash("Слишком большое количество инвентаря!", 'warning')
        return redirect(url_for('request.requests'))
    except Exception as e:
        logger.error(f"Error approving request: {e}")
        db.session.rollback()
        return redirect(url_for('request.requests'))


# deny request
@module.route('/deny/<int:id>')
@login_required
@is_admin
def deny_request(id):
    request: Request = Request.query.filter_by(id=id).first()
    request.deny_request()
    return redirect(url_for('request.requests'))