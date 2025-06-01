#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for å opprette en admin-bruker i NotatWeb-databasen
"""

import sys
import os
sys.path.append('app')

from app import app, db, Bruker
from werkzeug.security import generate_password_hash

def opprett_admin():
    with app.app_context():
        # Sjekk om admin-bruker allerede eksisterer
        admin = Bruker.query.filter_by(brukernavn='admin').first()
        if admin:
            print("Admin-bruker eksisterer allerede")
            return
        
        # Opprett admin-bruker
        admin_bruker = Bruker(
            brukernavn='admin',
            passord_hash=generate_password_hash('admin123'),
            er_admin=True
        )
        
        db.session.add(admin_bruker)
        db.session.commit()
        
        print("Admin-bruker opprettet!")
        print("Brukernavn: admin")
        print("Passord: admin123")

if __name__ == '__main__':
    opprett_admin()
