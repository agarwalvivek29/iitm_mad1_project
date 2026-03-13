from flask import Blueprint, render_template
from flask_login import login_required

from utils import librarian_required

librarian_bp = Blueprint('librarian', __name__, url_prefix='/librarian')


@librarian_bp.route('/dashboard')
@login_required
@librarian_required
def dashboard():
    return render_template('librarian/dashboard.html')
