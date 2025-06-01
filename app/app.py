from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from models import db, Bruker, Notat

# Last inn miljøvariabler fra .env-filen for sikker konfigurasjon
load_dotenv()

app = Flask(__name__)

# Database og sikkerhetskonfigurasjon
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DATABASE')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# Initialiser databasetilkobling og migrering
db.init_app(app)
migrate = Migrate(app, db)

# Konfigurer JWT (JSON Web Token) for autentisering
jwt = JWTManager(app)

@jwt.user_identity_loader
def user_identity_lookup(user):
    return str(user)

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return Bruker.query.get(int(identity))

# Konfigurer CORS (Cross-Origin Resource Sharing) for API-tilgang
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Importer blueprint-moduler for ulike API-endepunkter
from auth import auth_bp
from notes import notes_bp
from admin import admin_bp

# Registrer blueprints med deres respektive URL-prefikser
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(notes_bp, url_prefix='/api/notes')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

@app.route('/')
def index():
    return jsonify({"message": "Velkommen til NotatWeb API!"})

# Opprett databasetabeller ved oppstart hvis de ikke eksisterer
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
