from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    from models import User, Section, Book, BookRequest, Feedback

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    def index():
        return render_template('index.html')

    from routes.auth import auth_bp, seed_admin
    from routes.user import user_bp
    from routes.librarian import librarian_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(librarian_bp)
    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()
        seed_admin()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
