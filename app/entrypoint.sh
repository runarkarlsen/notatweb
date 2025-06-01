#!/bin/bash
set -e

echo "Starting NotatWeb API..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! python -c "
import mysql.connector
import os
import time
try:
    conn = mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST', 'db'),
        user=os.environ.get('MYSQL_USER', 'notatweb_user'),
        password=os.environ.get('MYSQL_PASSWORD', 'notatweb_password'),
        database=os.environ.get('MYSQL_DATABASE', 'notatweb')
    )
    conn.close()
    print('Database is ready!')
except:
    exit(1)
" 2>/dev/null; do
    echo "Database not ready yet, waiting..."
    sleep 2
done

echo "Database is ready!"

# Initialize database tables and create/update admin user
echo "Initializing database and admin user..."
python -c "
import sys
import os
from app import app, db
from models import Bruker
from werkzeug.security import generate_password_hash

with app.app_context():
    # Create tables if they don't exist
    db.create_all()
    
    # Check if admin user exists
    admin = Bruker.query.filter_by(brukernavn='admin').first()
    
    if admin:
        # Update existing admin user with correct password hash
        admin.passord_hash = generate_password_hash('admin123')
        admin.er_admin = True
        db.session.commit()
        print('Admin user updated with correct password hash')
    else:
        # Create new admin user
        admin_bruker = Bruker(
            brukernavn='admin',
            passord_hash=generate_password_hash('admin123'),
            er_admin=True
        )
        db.session.add(admin_bruker)
        db.session.commit()
        print('Admin user created successfully')
    
    print('Admin credentials:')
    print('Username: admin')
    print('Password: admin123')
"

echo "Starting Flask application..."
exec python app.py
