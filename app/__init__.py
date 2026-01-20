from flask import Flask,render_template
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_migrate import Migrate
from flask_login import LoginManager,login_user

#creating instances of class
moment = Moment()
bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()
login_manager=LoginManager()



# #configuration
# app.config['SECRET_KEY']='hard to guess string'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_data.sqlite'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #ye kya krta hai ab?



def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    migrate.init_app(app,db)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .models import User,Blog #why did i put it here to avoid circular import and that alembic thing otherwise it wont migrate database
    # print("Using DB:", app.config['SQLALCHEMY_DATABASE_URI']) #for finding the Database location and name

    login_manager.login_view='auth.login'
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app