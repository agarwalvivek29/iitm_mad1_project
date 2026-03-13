from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def librarian_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'librarian':
            flash('Librarian access required.', 'danger')
            return redirect(url_for('auth.librarian_login'))
        return f(*args, **kwargs)
    return decorated


def user_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'user':
            flash('Please log in as a user.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated
