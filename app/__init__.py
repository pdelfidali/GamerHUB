import os.path

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from flask_login import LoginManager
from flask_moment import Moment

bootstrap = Bootstrap()
db = SQLAlchemy()
basedir = Path(__file__).parent.absolute()
login_manager = LoginManager()
moment = Moment()

def create_app():
    app = Flask(__name__)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)

    app.config['SECRET_KEY'] = 'bedoes'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/')
    def index():
        return render_template('index.html')

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from app.announce import announce as announce_blueprint
    app.register_blueprint(announce_blueprint)

    from app.user import user as user_blueprint
    app.register_blueprint(user_blueprint)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    @app.errorhandler(401)
    def unauthorized(e):
        return render_template('401.html'), 401

    return app
