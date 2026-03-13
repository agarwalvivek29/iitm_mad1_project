from functools import wraps

from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user

from app import db
from models import Section, Book, BookRequest, Feedback

api_bp = Blueprint('api', __name__, url_prefix='/api')


def api_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key and api_key == current_app.config['API_KEY']:
            return f(*args, **kwargs)
        if current_user.is_authenticated and current_user.role == 'librarian':
            return f(*args, **kwargs)
        return jsonify({'error': 'Unauthorized'}), 401
    return decorated


# --- Sections API ---

@api_bp.route('/sections', methods=['GET'])
@api_auth_required
def list_sections():
    sections = Section.query.all()
    return jsonify([
        {
            'id': s.id,
            'name': s.name,
            'description': s.description,
            'date_created': s.date_created.isoformat(),
            'book_count': len(s.books),
        }
        for s in sections
    ])


@api_bp.route('/sections', methods=['POST'])
@api_auth_required
def create_section():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'name is required'}), 400

    if Section.query.filter_by(name=name).first():
        return jsonify({'error': 'Section with this name already exists'}), 400

    section = Section(name=name, description=data.get('description', ''))
    db.session.add(section)
    db.session.commit()
    return jsonify({
        'id': section.id,
        'name': section.name,
        'description': section.description,
        'date_created': section.date_created.isoformat(),
    }), 201


@api_bp.route('/sections/<int:section_id>', methods=['GET'])
@api_auth_required
def get_section(section_id):
    section = db.session.get(Section, section_id)
    if not section:
        return jsonify({'error': 'Section not found'}), 404
    return jsonify({
        'id': section.id,
        'name': section.name,
        'description': section.description,
        'date_created': section.date_created.isoformat(),
        'books': [
            {
                'id': b.id,
                'name': b.name,
                'author': b.author,
                'num_pages': b.num_pages,
            }
            for b in section.books
        ],
    })


@api_bp.route('/sections/<int:section_id>', methods=['PUT'])
@api_auth_required
def update_section(section_id):
    section = db.session.get(Section, section_id)
    if not section:
        return jsonify({'error': 'Section not found'}), 404

    data = request.get_json(silent=True) or {}
    if 'name' in data:
        name = (data['name'] or '').strip()
        if not name:
            return jsonify({'error': 'name cannot be empty'}), 400
        existing = Section.query.filter_by(name=name).first()
        if existing and existing.id != section.id:
            return jsonify({'error': 'Section with this name already exists'}), 400
        section.name = name
    if 'description' in data:
        section.description = data['description']

    db.session.commit()
    return jsonify({
        'id': section.id,
        'name': section.name,
        'description': section.description,
        'date_created': section.date_created.isoformat(),
    })


@api_bp.route('/sections/<int:section_id>', methods=['DELETE'])
@api_auth_required
def delete_section(section_id):
    section = db.session.get(Section, section_id)
    if not section:
        return jsonify({'error': 'Section not found'}), 404

    for book in section.books:
        book.section_id = None
    db.session.delete(section)
    db.session.commit()
    return jsonify({'message': 'Section deleted'})


# --- Books API ---

@api_bp.route('/books', methods=['GET'])
@api_auth_required
def list_books():
    query = Book.query
    section_id = request.args.get('section_id', type=int)
    author = request.args.get('author', '').strip()
    if section_id is not None:
        query = query.filter_by(section_id=section_id)
    if author:
        query = query.filter(Book.author.ilike(f'%{author}%'))
    books = query.all()
    return jsonify([
        {
            'id': b.id,
            'name': b.name,
            'author': b.author,
            'content': b.content,
            'num_pages': b.num_pages,
            'section_id': b.section_id,
            'date_added': b.date_added.isoformat(),
            'avg_rating': round(b.avg_rating, 2),
        }
        for b in books
    ])


@api_bp.route('/books', methods=['POST'])
@api_auth_required
def create_book():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    author = (data.get('author') or '').strip()
    content = (data.get('content') or '').strip()

    if not name or not author or not content:
        return jsonify({'error': 'name, author, and content are required'}), 400

    section_id = data.get('section_id')
    if section_id is not None:
        if not db.session.get(Section, section_id):
            return jsonify({'error': 'Section not found'}), 400

    book = Book(
        name=name,
        author=author,
        content=content,
        num_pages=data.get('num_pages', 0),
        section_id=section_id,
    )
    db.session.add(book)
    db.session.commit()
    return jsonify({
        'id': book.id,
        'name': book.name,
        'author': book.author,
        'content': book.content,
        'num_pages': book.num_pages,
        'section_id': book.section_id,
        'date_added': book.date_added.isoformat(),
    }), 201


@api_bp.route('/books/<int:book_id>', methods=['GET'])
@api_auth_required
def get_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify({
        'id': book.id,
        'name': book.name,
        'author': book.author,
        'content': book.content,
        'num_pages': book.num_pages,
        'section_id': book.section_id,
        'section_name': book.section.name if book.section else None,
        'date_added': book.date_added.isoformat(),
        'avg_rating': round(book.avg_rating, 2),
    })


@api_bp.route('/books/<int:book_id>', methods=['PUT'])
@api_auth_required
def update_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    data = request.get_json(silent=True) or {}
    if 'name' in data:
        name = (data['name'] or '').strip()
        if not name:
            return jsonify({'error': 'name cannot be empty'}), 400
        book.name = name
    if 'author' in data:
        author = (data['author'] or '').strip()
        if not author:
            return jsonify({'error': 'author cannot be empty'}), 400
        book.author = author
    if 'content' in data:
        content = (data['content'] or '').strip()
        if not content:
            return jsonify({'error': 'content cannot be empty'}), 400
        book.content = content
    if 'num_pages' in data:
        book.num_pages = data['num_pages']
    if 'section_id' in data:
        sid = data['section_id']
        if sid is not None and not db.session.get(Section, sid):
            return jsonify({'error': 'Section not found'}), 400
        book.section_id = sid

    db.session.commit()
    return jsonify({
        'id': book.id,
        'name': book.name,
        'author': book.author,
        'content': book.content,
        'num_pages': book.num_pages,
        'section_id': book.section_id,
        'date_added': book.date_added.isoformat(),
    })


@api_bp.route('/books/<int:book_id>', methods=['DELETE'])
@api_auth_required
def delete_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    BookRequest.query.filter_by(book_id=book_id).delete()
    Feedback.query.filter_by(book_id=book_id).delete()
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted'})
