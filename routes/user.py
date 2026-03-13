from datetime import datetime, timezone

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from models import Book, BookRequest, Feedback, Section
from utils import user_required

user_bp = Blueprint('user', __name__, url_prefix='/user')

MAX_ACTIVE_BOOKS = 5


@user_bp.before_request
def expire_overdue_books():
    if not current_user.is_authenticated or current_user.role != 'user':
        return
    now = datetime.now(timezone.utc)
    overdue = BookRequest.query.filter(
        BookRequest.user_id == current_user.id,
        BookRequest.status == 'approved',
        BookRequest.return_date < now
    ).all()
    for req in overdue:
        req.status = 'expired'
    if overdue:
        db.session.commit()


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


@user_bp.route('/book/<int:book_id>/request', methods=['POST'])
@login_required
@user_required
def request_book(book_id):
    book = Book.query.get_or_404(book_id)

    existing = BookRequest.query.filter(
        BookRequest.user_id == current_user.id,
        BookRequest.book_id == book_id,
        BookRequest.status.in_(['pending', 'approved'])
    ).first()
    if existing:
        flash('You already have an active or pending request for this book.', 'warning')
        return redirect(url_for('user.book_detail', book_id=book_id))

    active_count = BookRequest.query.filter_by(
        user_id=current_user.id, status='approved'
    ).count()
    if active_count >= MAX_ACTIVE_BOOKS:
        flash(f'You already have {MAX_ACTIVE_BOOKS} active books. Return one before requesting another.', 'warning')
        return redirect(url_for('user.book_detail', book_id=book_id))

    req = BookRequest(
        user_id=current_user.id,
        book_id=book_id,
        status='pending'
    )
    db.session.add(req)
    db.session.commit()
    flash(f'Request for "{book.name}" submitted successfully!', 'success')
    return redirect(url_for('user.book_detail', book_id=book_id))


@user_bp.route('/book/<int:book_id>/return', methods=['POST'])
@login_required
@user_required
def return_book(book_id):
    book = Book.query.get_or_404(book_id)

    req = BookRequest.query.filter_by(
        user_id=current_user.id, book_id=book_id, status='approved'
    ).first()
    if not req:
        flash('No active issue found for this book.', 'danger')
        return redirect(url_for('user.dashboard'))

    req.status = 'returned'
    db.session.commit()
    flash(f'You have returned "{book.name}".', 'success')
    return redirect(url_for('user.dashboard'))


@user_bp.route('/book/<int:book_id>/read')
@login_required
@user_required
def read_book(book_id):
    book = Book.query.get_or_404(book_id)

    req = BookRequest.query.filter_by(
        user_id=current_user.id, book_id=book_id, status='approved'
    ).first()
    if not req:
        flash('You do not have active access to this book.', 'danger')
        return redirect(url_for('user.book_detail', book_id=book_id))

    return render_template('user/read_book.html', book=book)
