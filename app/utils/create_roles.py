from app import db, logger
from app.models import Role


def create_roles():
    """
    Создаёт в БД роли пользователей
    """
    need_msg = False
    roles = ['user', 'admin']

    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name)
            db.session.add(role)
            need_msg = True

    if need_msg:
        db.session.commit()
        logger.info("Roles successfully added.")
