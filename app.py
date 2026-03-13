from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # Will load from User model once models.py exists (issue #2)
        return None

    @app.route('/')
    def index():
        return render_template('index.html')

    # Blueprints will be registered here in later issues:
    # from routes.auth import auth_bp
    # from routes.librarian import librarian_bp
    # from routes.user import user_bp

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
