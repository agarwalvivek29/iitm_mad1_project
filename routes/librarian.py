from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required

from app import db
from models import Section, Book, BookRequest, Feedback
from utils import librarian_required

librarian_bp = Blueprint('librarian', __name__, url_prefix='/librarian')


@librarian_bp.route('/dashboard')
@login_required
@librarian_required
def dashboard():
    total_sections = Section.query.count()
    total_books = Book.query.count()
    active_issues = BookRequest.query.filter_by(status='approved').count()
    pending_requests = BookRequest.query.filter_by(status='pending').all()
    active_issues_list = BookRequest.query.filter_by(status='approved') \
        .order_by(BookRequest.date_issued.desc()).all()
    return render_template('librarian/dashboard.html',
                           total_sections=total_sections,
                           total_books=total_books,
                           active_issues=active_issues,
                           pending_requests=pending_requests,
                           active_issues_list=active_issues_list)


@librarian_bp.route('/requests/<int:req_id>/approve', methods=['POST'])
@login_required
@librarian_required
def approve_request(req_id):
    req = BookRequest.query.get_or_404(req_id)
    if req.status != 'pending':
        flash('Request is no longer pending.', 'warning')
        return redirect(url_for('librarian.dashboard'))
    req.status = 'approved'
    req.date_issued = datetime.utcnow()
    req.return_date = datetime.utcnow() + timedelta(days=current_app.config['BOOK_LOAN_DAYS'])
    db.session.commit()
    flash('Request approved.', 'success')
    return redirect(url_for('librarian.dashboard'))


@librarian_bp.route('/requests/<int:req_id>/reject', methods=['POST'])
@login_required
@librarian_required
def reject_request(req_id):
    req = BookRequest.query.get_or_404(req_id)
    if req.status != 'pending':
        flash('Request is no longer pending.', 'warning')
        return redirect(url_for('librarian.dashboard'))
    req.status = 'rejected'
    db.session.commit()
    flash('Request rejected.', 'info')
    return redirect(url_for('librarian.dashboard'))


@librarian_bp.route('/requests/<int:req_id>/revoke', methods=['POST'])
@login_required
@librarian_required
def revoke_request(req_id):
    req = BookRequest.query.get_or_404(req_id)
    if req.status != 'approved':
        flash('Only approved issues can be revoked.', 'warning')
        return redirect(url_for('librarian.dashboard'))
    req.status = 'revoked'
    db.session.commit()
    flash('Book access revoked.', 'info')
    return redirect(url_for('librarian.dashboard'))


@librarian_bp.route('/sections')
@login_required
@librarian_required
def sections():
    all_sections = Section.query.order_by(Section.date_created.desc()).all()
    return render_template('librarian/sections.html', sections=all_sections)


@librarian_bp.route('/sections/create', methods=['GET', 'POST'])
@login_required
@librarian_required
def create_section():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Section name is required.', 'danger')
            return render_template('librarian/section_form.html', section=None)

        if len(name) > 100:
            flash('Section name must be 100 characters or fewer.', 'danger')
            return render_template('librarian/section_form.html', section=None)

        if Section.query.filter_by(name=name).first():
            flash('A section with that name already exists.', 'danger')
            return render_template('librarian/section_form.html', section=None)

        section = Section(name=name, description=description)
        db.session.add(section)
        db.session.commit()
        flash('Section created successfully.', 'success')
        return redirect(url_for('librarian.sections'))

    return render_template('librarian/section_form.html', section=None)


@librarian_bp.route('/sections/<int:section_id>/edit', methods=['GET', 'POST'])
@login_required
@librarian_required
def edit_section(section_id):
    section = Section.query.get_or_404(section_id)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Section name is required.', 'danger')
            return render_template('librarian/section_form.html', section=section)

        if len(name) > 100:
            flash('Section name must be 100 characters or fewer.', 'danger')
            return render_template('librarian/section_form.html', section=section)

        existing = Section.query.filter_by(name=name).first()
        if existing and existing.id != section.id:
            flash('A section with that name already exists.', 'danger')
            return render_template('librarian/section_form.html', section=section)

        section.name = name
        section.description = description
        db.session.commit()
        flash('Section updated successfully.', 'success')
        return redirect(url_for('librarian.sections'))

    return render_template('librarian/section_form.html', section=section)


@librarian_bp.route('/sections/<int:section_id>/delete', methods=['POST'])
@login_required
@librarian_required
def delete_section(section_id):
    section = Section.query.get_or_404(section_id)

    book_count = len(section.books)
    if book_count > 0:
        for book in section.books:
            book.section_id = None
        flash(
            f'Section "{section.name}" deleted. {book_count} book(s) were unassigned from this section.',
            'warning',
        )
    else:
        flash(f'Section "{section.name}" deleted.', 'success')

    db.session.delete(section)
    db.session.commit()
    return redirect(url_for('librarian.sections'))


@librarian_bp.route('/books')
@login_required
@librarian_required
def books():
    section_id = request.args.get('section_id', type=int)
    query = Book.query
    if section_id:
        query = query.filter_by(section_id=section_id)
    all_books = query.order_by(Book.date_added.desc()).all()
    all_sections = Section.query.order_by(Section.name).all()
    return render_template('librarian/books.html', books=all_books,
                           sections=all_sections, selected_section=section_id)


@librarian_bp.route('/books/create', methods=['GET', 'POST'])
@login_required
@librarian_required
def create_book():
    all_sections = Section.query.order_by(Section.name).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        author = request.form.get('author', '').strip()
        content = request.form.get('content', '').strip()
        section_id = request.form.get('section_id', type=int)
        num_pages = request.form.get('num_pages', '').strip()

        if not name:
            flash('Book name is required.', 'danger')
            return render_template('librarian/book_form.html', book=None, sections=all_sections)

        if not author:
            flash('Author is required.', 'danger')
            return render_template('librarian/book_form.html', book=None, sections=all_sections)

        if not content:
            flash('Content is required.', 'danger')
            return render_template('librarian/book_form.html', book=None, sections=all_sections)

        pages = 0
        if num_pages:
            try:
                pages = int(num_pages)
                if pages < 0:
                    flash('Number of pages must be a non-negative integer.', 'danger')
                    return render_template('librarian/book_form.html', book=None, sections=all_sections)
            except ValueError:
                flash('Number of pages must be a non-negative integer.', 'danger')
                return render_template('librarian/book_form.html', book=None, sections=all_sections)

        if section_id and not Section.query.get(section_id):
            section_id = None

        book = Book(name=name, author=author, content=content,
                    num_pages=pages, section_id=section_id)
        db.session.add(book)
        db.session.commit()
        flash('Book created successfully.', 'success')
        return redirect(url_for('librarian.books'))

    return render_template('librarian/book_form.html', book=None, sections=all_sections)


@librarian_bp.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
@librarian_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    all_sections = Section.query.order_by(Section.name).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        author = request.form.get('author', '').strip()
        content = request.form.get('content', '').strip()
        section_id = request.form.get('section_id', type=int)
        num_pages = request.form.get('num_pages', '').strip()

        if not name:
            flash('Book name is required.', 'danger')
            return render_template('librarian/book_form.html', book=book, sections=all_sections)

        if not author:
            flash('Author is required.', 'danger')
            return render_template('librarian/book_form.html', book=book, sections=all_sections)

        if not content:
            flash('Content is required.', 'danger')
            return render_template('librarian/book_form.html', book=book, sections=all_sections)

        pages = 0
        if num_pages:
            try:
                pages = int(num_pages)
                if pages < 0:
                    flash('Number of pages must be a non-negative integer.', 'danger')
                    return render_template('librarian/book_form.html', book=book, sections=all_sections)
            except ValueError:
                flash('Number of pages must be a non-negative integer.', 'danger')
                return render_template('librarian/book_form.html', book=book, sections=all_sections)

        if section_id and not Section.query.get(section_id):
            section_id = None

        book.name = name
        book.author = author
        book.content = content
        book.num_pages = pages
        book.section_id = section_id
        db.session.commit()
        flash('Book updated successfully.', 'success')
        return redirect(url_for('librarian.books'))

    return render_template('librarian/book_form.html', book=book, sections=all_sections)


@librarian_bp.route('/books/<int:book_id>/delete', methods=['POST'])
@login_required
@librarian_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    Feedback.query.filter_by(book_id=book.id).delete()
    BookRequest.query.filter_by(book_id=book.id).delete()
    db.session.delete(book)
    db.session.commit()
    flash(f'Book "{book.name}" deleted.', 'success')
    return redirect(url_for('librarian.books'))
