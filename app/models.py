from datetime import datetime

import sqlalchemy as sa
from enum import Enum
import sqlalchemy.orm as orm
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


# classes for defining different enum type
class RequestState(Enum):
    PENDING = 'pending'
    DENIED = 'denied'
    APPROVED = 'approved'


class RequestType(Enum):
    REPAIR = 'repair'
    TAKE = 'take'
    CHANGE = 'change'


class ItemState(Enum):
    NEW = 'new'
    USED = 'used'
    BROKEN = 'broken'


### SQLAlchemy models

# model for user roles (user or admin)
class Role(db.Model):
    __tablename__ = 'roles'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, unique=True, nullable=False)

    users = orm.relationship('User', back_populates='role')


# basic user model
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String, unique=True, nullable=False)
    hashed_password = sa.Column(sa.String, nullable=False)
    role_id = sa.Column(sa.Integer, sa.ForeignKey('roles.id'), nullable=False, default=1)
    created_date = sa.Column(sa.DateTime, default=datetime.utcnow)

    role = orm.relationship('Role', back_populates='users')
    requests = orm.relationship("Request", back_populates="user")
    requested_items = orm.relationship("RequestedItem", back_populates="user")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


# model of inventory item
class Item(db.Model):
    __tablename__ = 'items'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    state = sa.Column(sa.Enum(ItemState), nullable=False, default=ItemState.NEW)
    total_quantity = sa.Column(sa.Integer, nullable=False)
    available_quantity = sa.Column(sa.Integer, nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)

    requests = orm.relationship('Request', back_populates='item')
    requested_items = orm.relationship("RequestedItem", back_populates="item")

    def change_item(self, name, state, quantity):
        if quantity < (self.total_quantity - self.available_quantity):
            raise ValueError
        self.name = name
        self.state = state
        self.available_quantity -= self.total_quantity - quantity
        self.total_quantity = quantity
        db.session.commit()

    def assign_item(self, quantity, user_id):
        if quantity > self.available_quantity or quantity < 0:
            raise ValueError
        self.available_quantity -= quantity
        requested_item: RequestedItem = RequestedItem.query.filter_by(user_id=user_id, item_id=self.id).first()
        if requested_item:
            requested_item.quantity += quantity
        else:
            requested_item: RequestedItem = RequestedItem(user_id=user_id,
                                                          item_id=self.id,
                                                          quantity=quantity)
            db.session.add(requested_item)
        db.session.commit()


# model for items, which were transferred to user
class RequestedItem(db.Model):
    __tablename__ = 'requested_items'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    quantity = sa.Column(sa.Integer, nullable=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    item_id = sa.Column(sa.Integer, sa.ForeignKey('items.id'), nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)

    user = orm.relationship('User', back_populates='requested_items')
    item = orm.relationship('Item', back_populates='requested_items')

# model of request (for example request to repair item)
class Request(db.Model):
    __tablename__ = 'requests'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    quantity = sa.Column(sa.Integer, nullable=False)
    state = sa.Column(sa.Enum(RequestState), default=RequestState.PENDING, nullable=False)
    type = sa.Column(sa.Enum(RequestType), default=RequestType.REPAIR, nullable=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    item_id = sa.Column(sa.Integer, sa.ForeignKey('items.id'), nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)

    user = orm.relationship('User', back_populates='requests')
    item = orm.relationship('Item', back_populates='requests')

    @classmethod
    def create_request(cls, user_id, item_id, type, quantity):
        item: Item = Item.query.get(item_id)
        if quantity > item.available_quantity:
            raise ValueError
        if type.value == 'repair' or type.value == 'change':
            request = Request.query.filter_by(item_id=item_id, user_id=user_id, type=type,
                                              state=RequestState.PENDING).first()
            if request:
                raise ValueError
        request = Request(user_id=user_id, item_id=item_id, type=type, quantity=quantity)
        db.session.add(request)
        db.session.commit()

    def approve_request(self):
        if self.state.value != 'pending':
            raise ValueError
        if self.quantity > self.item.available_quantity:
            self.deny_request()
            raise ValueError
        self.state = RequestState.APPROVED
        self.item.available_quantity -= self.quantity
        requested_item: RequestedItem = RequestedItem.query.filter_by(user_id=self.user_id, item_id=self.item_id).first()
        if requested_item:
            requested_item.quantity += self.quantity
        else:
            requested_item: RequestedItem = RequestedItem(user_id=self.user_id,
                                                          item_id=self.item_id,
                                                          quantity=self.quantity)
            db.session.add(requested_item)
        db.session.commit()

    def deny_request(self):
        if self.state.value != 'pending':
            raise ValueError
        self.state = RequestState.DENIED
        db.session.commit()

# model for purchases
class Purchase(db.Model):
    __tablename__ = 'purchases'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False)
    supplier = sa.Column(sa.String, nullable=False)
    price = sa.Column(sa.Float, nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)