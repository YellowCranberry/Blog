from flask import Flask, render_template
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_migrate import Migrate
from flask_login import LoginManager, login_user
from flask_ckeditor import CKEditor
from flask_caching import Cache
from dev.flask_ext import HybridSearch


# Creating instances of extension classes.
# These are module-level singletons — they are attached to the app via init_app().
moment = Moment()
bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
ckeditor = CKEditor()
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

# The HybridSearch extension — uses lazy loading.
# The embedding model is NOT loaded here; it loads on the first search/ingest call.
# This makes `flask run` fast even on slow machines.
search = HybridSearch()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    ckeditor.init_app(app)
    cache.init_app(app)

    # Register the HybridSearch extension.
    # It reads HYBRID_SEARCH_DB_URL and other settings from app.config.
    search.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # Import models here to avoid circular imports and ensure Alembic sees them
    from .models import User, Blog

    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app