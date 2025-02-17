from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
# Configure SQLite database with absolute path
import os
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'library.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize database within application context
with app.app_context():
    db.create_all()

# Models
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    borrowed_books = db.relationship('Borrows', backref='user', lazy=True)

class Authors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    yearOfBirth = db.Column(db.Integer, nullable=False)
    books = db.relationship('Books', backref='author', lazy=True)

class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    borrows = db.relationship('Borrows', backref='book', lazy=True)

class Borrows(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    isReturned = db.Column(db.Boolean, default=False)

# CRUD Routes for Users
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if "name" not in data or "email" not in data:
        return jsonify({"message": "Name and Email are required"}), 400
    new_user = Users(name=data['name'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        "message": "User successfully created.",
        "newUser": {
            "id": new_user.id,
            "userName": new_user.name,
            "email": new_user.email
        }
    }), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = Users.query.all()
    if not users:
        return jsonify({"message": "No users found"}), 404
    output = []
    for user in users:
        user_data = {'id': user.id, 'name': user.name, 'email': user.email}
        output.append(user_data)
    return jsonify({ "message": "success", "data": output}), 200

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = Users.query.get_or_404(id)
    return jsonify({
        "message": "success",
        "user": {
            "id": user.id,
            "userName": user.name,
            "email": user.email
        }
    }), 200

@app.route('/users/<id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    if "name" not in data or "email" not in data:
        return jsonify({"message": "Name and Email are required"}), 400
    user = Users.query.get_or_404(id)
    user.name = data['name']
    user.email = data['email']
    db.session.commit()
    return jsonify({
        "message": "User successfully updated.",
        "user": {
            "id": user.id,
            "userName": user.name,
            "email": user.email
        }
    }), 200

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = Users.query.get_or_404(id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User successfully deleted!"}), 200

# CRUD Routes for Authors
@app.route('/authors', methods=['POST'])
def create_author():
    data = request.get_json()
    if "name" not in data or "yearOfBirth" not in data:
        return jsonify({"message": "Name and yearOfBirth are required"}), 400
    new_author = Authors(name=data['name'], yearOfBirth=data['yearOfBirth'])
    db.session.add(new_author)
    db.session.commit()
    return jsonify({
        "message": "Author successfully created.",
        "author": {
            "id": new_author.id,
            "name": new_author.name,
            "yearOfBirth": new_author.yearOfBirth
        }
    }), 201

@app.route('/authors', methods=['GET'])
def get_authors():
    authors = Authors.query.all()
    if not authors:
        return jsonify({"message": "No authors found"}), 404
    output = []
    for author in authors:
        author_data = {'id': author.id, 'name': author.name, 'yearOfBirth': author.yearOfBirth}
        output.append(author_data)
    return jsonify({ "message": "success", "data": output}), 200

@app.route('/authors/<int:id>', methods=['GET'])
def get_author(id):
    author = Authors.query.get_or_404(id)
    return jsonify({
        "message": "success",
        "author": {
            "id": author.id,
            "name": author.name,
            "yearOfBirth": author.yearOfBirth
        }
    }), 200

@app.route('/authors/<id>', methods=['PUT'])
def update_author(id):
    data = request.get_json()
    if "name" not in data or "yearOfBirth" not in data:
        return jsonify({"message": "Name and yearOfBirth are required"}), 400
    author = Authors.query.get_or_404(id)
    author.name = data['name']
    author.yearOfBirth = data['yearOfBirth']
    db.session.commit()
    return jsonify({
        "message": "Author successfully updated.",
        "author": {
            "id": author.id,
            "name": author.name,
            "yearOfBirth": author.yearOfBirth
        }
    }), 200

@app.route('/authors/<int:id>', methods=['DELETE'])
def delete_author(id):
    author = Authors.query.get_or_404(id)
    if not author:
        return jsonify({"message": "Author not found"}), 404
    db.session.delete(author)
    db.session.commit()
    return jsonify({"message": "Author successfully deleted!"}), 200

# CRUD Routes for Books
@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    if "title" not in data or "author_id" not in data:
        return jsonify({"message": "Title and author_id are required"}), 400
    author = Authors.query.get(data['author_id'])
    if not author:
        return jsonify({"message": "Author not found"}), 404
    new_book = Books(title=data['title'], author_id=data['author_id'])
    db.session.add(new_book)
    db.session.commit()
    return jsonify({
        "message": "Book successfully created.",
        "book": {
            "id": new_book.id,
            "title": new_book.title,
            "author_id": new_book.author_id
        }
    }), 201

@app.route('/books', methods=['GET'])
def get_books():
    books = Books.query.all()
    if not books:
        return jsonify({"message": "No books found"}), 404
    output = []
    for book in books:
        book_data = {'id': book.id, 'title': book.title, 'author_id': book.author_id}
        output.append(book_data)
    return jsonify({ "message": "success", "data": output}), 200

@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Books.query.get_or_404(id)
    return jsonify({
        "message": "success",
        "book": {
            "id": book.id,
            "title": book.title,
            "author_id": book.author_id
        }
    }), 200

@app.route('/books/<id>', methods=['PUT'])
def update_book(id):
    data = request.get_json()
    if "title" not in data or "author_id" not in data:
        return jsonify({"message": "Title and author_id are required"}), 400
    book = Books.query.get_or_404(id)
    book.title = data['title']
    book.author_id = data['author_id']
    db.session.commit()
    return jsonify({
        "message": "Book successfully updated.",
        "book": {
            "id": book.id,
            "title": book.title,
            "author_id": book.author_id
        }
    }), 200

@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Books.query.get_or_404(id)
    if not book:
        return jsonify({"message": "Book not found"}), 404
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book successfully deleted!"}), 200

# Borrowing Routes
@app.route('/borrow', methods=['POST'])
def borrow_book():
    data = request.get_json()
    if "user_id" not in data or "book_id" not in data:
        return jsonify({"message": "user_id and book_id are required"}), 400
    user = Users.query.get(data['user_id'])
    if not user:
        return jsonify({"message": "User not found"}), 404
    book = Books.query.get(data['book_id'])
    if not book:
        return jsonify({"message": "Book not found"}), 404
    # Check if book is already borrowed
    last_borrow = Borrows.query.filter_by(book_id=data['book_id']).order_by(Borrows.borrow_date.desc()).first()
    if last_borrow and not last_borrow.isReturned:
        return jsonify({"message": "Book is already borrowed"}), 400
    new_borrow = Borrows(user_id=data['user_id'], book_id=data['book_id'])
    db.session.add(new_borrow)
    db.session.commit()
    return jsonify({
        "message": "Book successfully borrowed",
        "borrow": {
            "id": new_borrow.id,
            "user_id": new_borrow.user_id,
            "book_id": new_borrow.book_id,
            "borrow_date": new_borrow.borrow_date,
            "isReturned": new_borrow.isReturned
        }
    }), 201

@app.route('/return/<int:id>', methods=['PATCH'])
def return_book(id):
    borrow = Borrows.query.get_or_404(id)
    if borrow.isReturned:
        return jsonify({"message": "Book is already returned"}), 400
    borrow.isReturned = True
    db.session.commit()
    return jsonify({
        "message": "Book successfully returned",
        "borrow": {
            "id": borrow.id,
            "user_id": borrow.user_id,
            "book_id": borrow.book_id,
            "borrow_date": borrow.borrow_date,
            "isReturned": borrow.isReturned
        }
    }), 200

@app.route('/borrows', methods=['GET'])
def get_borrows():
    borrows = Borrows.query.all()
    if not borrows:
        return jsonify({"message": "No borrow records found"}), 404
    output = []
    for borrow in borrows:
        borrow_data = {
            "id": borrow.id,
            "user_id": borrow.user_id,
            "book_id": borrow.book_id,
            "borrow_date": borrow.borrow_date,
            "isReturned": borrow.isReturned
        }
        output.append(borrow_data)
    return jsonify({ "message": "success", "data": output}), 200

if __name__ == '__main__':
    app.run(debug=True)
