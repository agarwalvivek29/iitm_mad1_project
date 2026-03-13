from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required

from app import db
from models import Section, Book, BookRequest
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
