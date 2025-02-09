from app import create_app, db, login_manager
from app.models import User
from app.utils.create_roles import create_roles


app = create_app()

with app.test_request_context():
    db.create_all()
    create_roles()

# set login manager user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)