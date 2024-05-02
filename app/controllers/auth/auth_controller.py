from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from app.models.users import User, db
from app.models.books import Book
from email_validator import validate_email, EmailNotValidError
from flask_bcrypt import Bcrypt
from app.models.revoked_tokens import RevokedTokenModel


auth = Blueprint('auth', __name__, url_prefix='/api/v1/auth')
bcrypt = Bcrypt()

@auth.route('/register', methods=['POST'])
def register():
    try:
        data = request.json

        # Extracting request data
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        contact = data.get('contact')
        email = data.get('email')
        user_type = data.get('user_type', 'user')  # Default to 'user'
        password = data.get('password')
        biography = data.get('biography', '') if user_type == 'author' else ''

        # Basic input validation
        required_fields = ['first_name', 'last_name', 'contact', 'password', 'email']
        if not all(data.get(field) for field in required_fields):
            return jsonify({'error': 'All fields are required'}), 400

        if len(password) < 6:
            return jsonify({'error': 'Password is too short'}), 400

        # Email validation 
        validate_email(email)

        # Check for uniqueness of email and contact separately
        if User.query.filter_by(email=email).first() is not None:
            return jsonify({'error': 'Email already exists'}), 409

        if User.query.filter_by(contact=contact).first() is not None:
            return jsonify({'error': 'Contact already exists'}), 409

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Creating a new user
        new_user = User(first_name=first_name, last_name=last_name, email=email,
                        contact=contact, password=hashed_password, user_type=user_type,
                        biography=biography)

        # Adding and committing to the database
        db.session.add(new_user)
        db.session.commit()

        # Building a response
        username = f"{new_user.first_name} {new_user.last_name}"

        return jsonify({
            'message': f'{username} has been successfully created as an {new_user.user_type}',
            'user': {
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'email': new_user.email,
                'contact': new_user.contact,
                'type': new_user.user_type,
                'biography': new_user.biography,
                'created_at': new_user.created_at,
            }
        }), 201

    except EmailNotValidError:
        return jsonify({'error': 'Email is not valid'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth.route('/users/', methods=['GET'])
@jwt_required()  # Only authenticated users can access this route
def get_all_users():
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user).first()
    if user.user_type != 'admin':
        return jsonify({'error': 'You are not authorized to access this route'}), 403

    users = User.query.all()
    output = []
    for user in users:
        user_data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'contact': user.contact,
            'user_type': user.user_type,
            'biography': user.biography
        }
        output.append(user_data)
    return jsonify({'users': output})

@auth.route('/user/<int:id>', methods=['GET'])
@jwt_required()  # Only authenticated users can access this route
def get_user(id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user).first()
    if user.user_type != 'admin' and user.id != id:
        return jsonify({'error': 'You are not authorized to access this user data'}), 403

    user = User.query.get_or_404(id)
    user_data = {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'contact': user.contact,
        'user_type': user.user_type,
        'biography': user.biography
    }
    return jsonify(user_data)

@auth.route('/user/<int:id>', methods=['PUT'])
@jwt_required()  # Only authenticated users can access this route
def update_user(id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user).first()
    if user.user_type != 'admin' and user.id != id:
        return jsonify({'error': 'You are not authorized to update this user'}), 403

    try:
        user = User.query.get_or_404(id)
        data = request.json
        user.email = data.get('email', user.email)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.contact = data.get('contact', user.contact)
        user.user_type = data.get('user_type', user.user_type)
        password = data.get('password')
        if password:
            user.password = bcrypt.generate_password_hash(password).decode('utf-8')
        user.biography = data.get('biography', user.biography)
        db.session.commit()
        return jsonify({'message': 'User updated successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth.route('/user/<int:id>', methods=['DELETE'])
@jwt_required()  # Only authenticated users can access this route
def delete_user(id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user).first()
    if user.user_type != 'admin' and user.id != id:
        return jsonify({'error': 'You are not authorized to delete this user'}), 403

    try:
        # Check if there are related records in the books table
        related_books = Book.query.filter_by(user_id=id).all()
        for book in related_books:
            db.session.delete(book)
        
        # Delete the user
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User and associated books deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete user', 'details': str(e)}), 500

@auth.route('/login', methods=['POST'])
def login():
    try:
        email = request.json.get('email')
        password = request.json.get('password')

        if not email or not password:
            return jsonify({'error': 'Missing email or password'}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not bcrypt.check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid password'}), 401

        # Password is correct, generate access token
        access_token = create_access_token(identity=user.id)
        return jsonify({'message': f'Login successful. You have logged in as {user.user_type}', 'access_token': access_token}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth.route('/logout', methods=['POST'])
@jwt_required()  # Only authenticated users can access this route
def logout():
    try:
        # Logout the user by invalidating the JWT token
        jti = get_jwt()['jti']
        revoked_token = RevokedTokenModel(jti=jti)
        db.session.add(revoked_token)
        db.session.commit()
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        return jsonify({'error':str(e)}),500