from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.role == 'librarian':
            return redirect(url_for('librarian.dashboard'))
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return redirect(url_for('auth.register'))

        user = User(username=username, role='user')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'librarian':
            return redirect(url_for('librarian.dashboard'))
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.login'))

        if user.role != 'user':
            flash('Please use the librarian login page.', 'warning')
            return redirect(url_for('auth.librarian_login'))

        login_user(user)
        flash('Logged in successfully.', 'success')
        return redirect(url_for('user.dashboard'))

    return render_template('auth/login.html')


@auth_bp.route('/librarian/login', methods=['GET', 'POST'])
def librarian_login():
    if current_user.is_authenticated:
        if current_user.role == 'librarian':
            return redirect(url_for('librarian.dashboard'))
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.librarian_login'))

        if user.role != 'librarian':
            flash('This account is not a librarian account.', 'danger')
            return redirect(url_for('auth.librarian_login'))

        login_user(user)
        flash('Logged in successfully.', 'success')
        return redirect(url_for('librarian.dashboard'))

    return render_template('auth/librarian_login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


def seed_admin():
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', role='librarian')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
