import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_debugtoolbar import DebugToolbarExtension

from dotenv import load_dotenv
from loguru import logger

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()

# Setup logger
logger.remove()
logger.add(
    "app.log",
    level="DEBUG",
    rotation="10 MB",
    compression="zip"
)
logger.add(
    sys.stdout,
    level="DEBUG"
)

def create_app():
    """
    Factory function to create a Flask application.
    """
    logger.info("Starting Flask application...")

    app = Flask(__name__)

    # get from .env app settings
    load_dotenv()
    settings = os.environ.get('APP_SETTINGS')
    if settings is None:
        logger.error(".env variable is not set.")
        sys.exit(1)
    app.config.from_object(settings)

    logger.info(f"Application use {settings}")

    if app.config['DEBUG']:
        DebugToolbarExtension(app)
        os.environ.setdefault("FLASK_DEBUG", "1")

    # Initialize extensions
    login_manager.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # register errors handler
    import app.modules.errors as errors
    app.register_blueprint(errors.module)

    ### register all app modules
    import app.modules.main as main
    app.register_blueprint(main.module)

    import app.modules.register as register
    app.register_blueprint(register.module)

    import app.modules.inventory as inventory
    app.register_blueprint(inventory.module)

    import app.modules.request as request
    app.register_blueprint(request.module)

    import app.modules.purchase as purchase
    app.register_blueprint(purchase.module)

    import app.modules.report as report
    app.register_blueprint(report.module)

    import app.api as api
    app.register_blueprint(api.module)

    logger.info("Flask application initialized successfully.")

    return app