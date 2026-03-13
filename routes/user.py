from datetime import datetime, timezone

from flask import Blueprint, render_template
from flask_login import current_user, login_required

from models import BookRequest
from utils import user_required

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/dashboard')
@login_required
@user_required
def dashboard():
    active_books = BookRequest.query.filter_by(
        user_id=current_user.id, status='approved'
    ).order_by(BookRequest.date_issued.desc()).all()

    pending_requests = BookRequest.query.filter_by(
        user_id=current_user.id, status='pending'
    ).all()

    history = BookRequest.query.filter(
        BookRequest.user_id == current_user.id,
        BookRequest.status.in_(['returned', 'revoked', 'expired', 'rejected'])
    ).order_by(BookRequest.date_requested.desc()).limit(10).all()

    now = datetime.now(timezone.utc)

    return render_template('user/dashboard.html',
                           active_books=active_books,
                           pending_requests=pending_requests,
                           history=history,
                           now=now)
