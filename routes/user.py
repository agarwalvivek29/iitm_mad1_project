from datetime import datetime, timezone

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from app import db

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


@user_bp.route('/search')
@login_required
@user_required
def search():
    q = request.args.get('q', '').strip()
    section_filter = request.args.get('section_id', type=int)

    sections = []
    books = []

    if q:
        sections = Section.query.filter(
            Section.name.ilike(f'%{q}%')
        ).all()

        book_query = Book.query.filter(
            db.or_(
                Book.name.ilike(f'%{q}%'),
                Book.author.ilike(f'%{q}%')
            )
        )
        if section_filter:
            book_query = book_query.filter_by(section_id=section_filter)
        books = book_query.all()

    all_sections = Section.query.order_by(Section.name).all()
    return render_template('user/search.html', q=q, sections=sections,
                           books=books, all_sections=all_sections,
                           section_filter=section_filter)
