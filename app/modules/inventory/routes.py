import copy

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.models import Item, ItemState, User, RequestedItem
from app import db, logger
from app.modules.request.forms import CreateRequestForm
from app.utils.is_admin import is_admin
from . import module, forms


# shows items
@module.route('/', methods=['GET'])
@login_required
def my_inventory():
    items = []
    available_items = []
    users = []
    form = forms.CreateItemForm()
    form2 = forms.ChangeItemForm()
    form3 = forms.AssignItemForm()
    form4 = CreateRequestForm()

    if current_user.role.name == 'admin':
        items = Item.query.all()
        users = [user for user in User.query.all() if user.role.name != 'admin']
    if current_user.role.name == 'user':
        requested_items = RequestedItem.query.filter_by(user_id=current_user.id).all()
        items = []
        for req_item in requested_items:
            item = copy.deepcopy(req_item.item)
            item.available_quantity = req_item.quantity
            items.append(item)
        available_items = Item.query.where(Item.available_quantity > 0).all()

    form3.user_id.choices = [(user.id, user.name) for user in users]

    return render_template('inventory/my_inventory.html', title='Доступный инвентарь', items=items, form=form,
                           form2=form2, form3=form3, form4=form4, users=users, available_items=available_items)

# adding new item to db
@module.route('/add_item', methods=['POST'])
@login_required
@is_admin
def add_item():
    form = forms.CreateItemForm()
    if form.quantity.data == 0:
        return redirect(url_for('inventory.my_inventory'))
    if form.validate_on_submit():
        logger.debug(f"Processing new inventory item: {form.name.data}")
        try:
            item = Item(
                name=form.name.data,
                total_quantity=form.quantity.data,
                available_quantity=form.quantity.data
            )
            db.session.add(item)
            db.session.commit()
            logger.info(f"Item {form.name.data} successfully added.")
        except Exception as e:
            logger.error(f"Error adding item {form.name.data}: {e}")
            db.session.rollback()
    return redirect(url_for('inventory.my_inventory'))

# changing infp about item in db
@module.route('/change_item/<int:id>', methods=['POST'])
@login_required
@is_admin
def change_item(id):
    form = forms.ChangeItemForm()
    if form.quantity.data == 0:
        flash("Слишком маленькое количество инвентаря!", 'warning')
        return redirect(url_for('inventory.my_inventory'))

    if form.validate_on_submit():
        logger.debug(f"Processing changing inventory item: {form.name.data}")
        try:
            if form.state.data == 'new':
                form.state.data = ItemState.NEW
            elif form.state.data == 'used':
                form.state.data = ItemState.USED
            elif form.state.data == 'broken':
                form.state.data = ItemState.BROKEN

            item: Item = Item.query.get(id)
            item.change_item(name=form.name.data,
                             quantity=form.quantity.data,
                             state=form.state.data)
            logger.info(f"Item {form.name.data} successfully added.")

        except ValueError:
            db.session.rollback()
            flash("Слишком маленькое количество инвентаря!", 'warning')
        except Exception as e:
            logger.error(f"Error adding item {form.name.data}: {e}")
            db.session.rollback()
    return redirect(url_for('inventory.my_inventory'))

# deleting item from db
@module.route('/delete_item/<int:id>')
@login_required
@is_admin
def delete_item(id):
    item: Item = Item.query.get(id)
    requested_items = item.requested_items
    for req_item in requested_items:
        db.session.delete(req_item)
    db.session.delete(item)
    db.session.commit()
    logger.debug(f"Successfully delete item {item.name}")
    return redirect(url_for('inventory.my_inventory'))


# assigning item to user
@module.route('/assign_item/<int:id>', methods=['POST'])
@login_required
@is_admin
def assign_item(id):
    form = forms.AssignItemForm()
    users = [user for user in User.query.all() if user.role.name != 'admin']

    form.user_id.choices = [(user.id, user.name) for user in users]
    if form.user_id.choices == [] or form.quantity.data == 0:
        return redirect(url_for('inventory.my_inventory'))
    if form.validate_on_submit():
        try:
            if form.user_id.data is None:
                return redirect(url_for('inventory.my_inventory'))
            item: Item = Item.query.get(id)
            item.assign_item(quantity=form.quantity.data,
                             user_id=form.user_id.data)

            logger.info(f"Item {item.name} assigned to user ID {form.user_id.data}.")
            return redirect(url_for('inventory.my_inventory'))
        except ValueError:
            db.session.rollback()
            flash("Слишком большое количество инвентаря!", 'warning')
            return redirect(url_for('inventory.my_inventory'))
        except Exception as e:
            logger.error(f"Error assigning item {id}: {e}")
            db.session.rollback()
            return redirect(url_for('inventory.my_inventory', message='Произошла ошибка назначения.'))

# assigning item to user
@module.route('/assign_item/<int:item_id>/remove/<int:user_id>')
@login_required
@is_admin
def remove_assign_item(item_id, user_id):
    requested_item: RequestedItem = RequestedItem.query.filter_by(item_id=item_id, user_id=user_id).first()
    requested_item.item.available_quantity += requested_item.quantity
    db.session.delete(requested_item)
    db.session.commit()
    logger.debug(f"Successfully delete assigning {requested_item.item.name}")
    return redirect(url_for('inventory.my_inventory'))
