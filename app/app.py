from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import os



db_user = os.getenv('DB_USER', 'postgres')
db_password = os.getenv('DB_PASSWORD', 'password')
db_host = os.getenv('DB_HOST', 'db')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME', 'postgres')

db_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

print(db_url)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
db = SQLAlchemy(app)
jwt = JWTManager(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_pseudonym = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

# Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'author': self.author,
            'isbn': self.isbn,
            'price': str(self.price)
        }


# API endpoints

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and (user.password == password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify(message='Invalid username or password'), 401


@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(
        author_pseudonym=data['author_pseudonym'],
        username=data['username'],
        password=data['password']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user_data = {
        'id': user.id,
        'author_pseudonym': user.author_pseudonym,
        'username': user.username
    }
    return jsonify(user_data), 200



@app.route('/books', methods=['POST'])
@jwt_required()
def create_book():
    data = request.json
    new_book = Book(title=data['title'],
                    description=data['description'],
                    author=data['author'],
                    isbn=data['isbn'],
                    price=data['price'])
    db.session.add(new_book)
    db.session.commit()
    return jsonify(message='Book created successfully'), 201

@app.route('/books', methods=['GET'])
@jwt_required()
def list_books():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books])

@app.route('/books/<int:book_id>', methods=['GET'])
@jwt_required()
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())

@app.route('/books/search', methods=['GET'])
@jwt_required()
def search_books():
    author = request.args.get('author')
    if author:
        books = Book.query.filter_by(author=author).all()
        return jsonify([book.to_dict() for book in books])
    else:
        return jsonify(message='Please provide an author parameter for search'), 400

@app.route('/books/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.json
    book.title = data['title']
    book.description = data['description']
    book.author = data['author']
    book.isbn = data['isbn']
    book.price = data['price']
    db.session.commit()
    return jsonify(message='Book details updated successfully')

@app.route('/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify(message='Book deleted successfully')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
