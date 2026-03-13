from datetime import datetime, timezone

from flask import Blueprint, render_template
from flask_login import current_user, login_required

from models import Book, BookRequest, Feedback, Section
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


@user_bp.route('/browse')
@login_required
@user_required
def browse():
    sections = Section.query.order_by(Section.date_created.desc()).all()
    recent_books = Book.query.order_by(Book.date_added.desc()).limit(5).all()
    return render_template('user/browse.html',
                           sections=sections,
                           recent_books=recent_books)


@user_bp.route('/section/<int:section_id>')
@login_required
@user_required
def section_detail(section_id):
    section = Section.query.get_or_404(section_id)
    books = Book.query.filter_by(section_id=section_id).order_by(Book.date_added.desc()).all()
    return render_template('user/section_detail.html',
                           section=section,
                           books=books)


@user_bp.route('/book/<int:book_id>')
@login_required
@user_required
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    feedbacks = Feedback.query.filter_by(book_id=book_id).order_by(Feedback.created_at.desc()).all()

    active_request = BookRequest.query.filter_by(
        user_id=current_user.id, book_id=book_id, status='approved'
    ).first()
    pending_request = BookRequest.query.filter_by(
        user_id=current_user.id, book_id=book_id, status='pending'
    ).first()

    if active_request:
        user_book_status = 'reading'
    elif pending_request:
        user_book_status = 'requested'
    else:
        user_book_status = 'available'

    return render_template('user/book_detail.html',
                           book=book,
                           feedbacks=feedbacks,
                           user_book_status=user_book_status)
