from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

# Initialiser utvidelser
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    # Last inn miljøvariabler fra .env
    load_dotenv()
    
    app = Flask(__name__)

    # Konfigurasjon
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DATABASE')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

    # Initialiser utvidelser med app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)

    with app.app_context():
        # Importer modeller og ruter
        from . import models
        from .auth import auth_bp
        from .notes import notes_bp
        from .admin import admin_bp

        # Registrer blueprints
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(notes_bp, url_prefix='/api/notes')
        app.register_blueprint(admin_bp, url_prefix='/api/admin')

        # Opprett databasetabeller
        db.create_all()

        return app
