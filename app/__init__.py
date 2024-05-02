from flask import Flask, jsonify, send_file
from flask_swagger_ui import get_swaggerui_blueprint
from app.extensions import migrate, db
from flask_sqlalchemy import SQLAlchemy

from app.controllers.auth.auth_controller import auth
from app.controllers.auth.book_controller import book_bp
from app.controllers.auth.company_controller import company_bp
from app.controllers.auth.revokedTokenController import revoked_tokens_bp

from flask_jwt_extended import JWTManager
from app.models.users import User
from app.models.companies import Company
from app.models.books import Book
import os

def create_app():  
    app = Flask(__name__)

    # Load configuration from the Config class
    app.config.from_object('config.Config')
    
    # Set the JWT secret key
    app.config['JWT_SECRET_KEY'] = 'jera256'
   
    # Initialize the Flask application with SQLAlchemy
    db.init_app(app)
    
    # Initialize JWTManager
    jwt = JWTManager(app)

    # Initialize Flask-Migrate for handling database migrations
    migrate.init_app(app, db)

    # Create database tables
    with app.app_context():
        db.create_all()
        # Bind metadata to the database engine
        db.metadata.create_all(bind=db.engine)

    # Register blueprints or routes here
    app.register_blueprint(auth)
    app.register_blueprint(book_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(revoked_tokens_bp)  
    
    # Serve Swagger UI
    SWAGGER_URL = '/api/doc'  # URL for accessing Swagger UI (usually /api/doc)
    API_URL = '/swagger.json' # URL for accessing Swagger JSON (usually /swagger.json)

    swagger_ui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  
        API_URL,
        config={  
            'app_name': "Authors API",
            'swagger': "2.0",
        }
    )

    app.register_blueprint(swagger_ui_blueprint)  # Register once without URL prefix
    
    @app.route('/')
    def home():
        return "AUTHORS API project set up 1"

    # Route for serving Swagger JSON
    @app.route('/swagger.json')
    def serve_swagger_json():
        swagger_file_path = os.path.join(app.root_path, 'swagger.json')
        return send_file(swagger_file_path, mimetype='application/json')

    return app