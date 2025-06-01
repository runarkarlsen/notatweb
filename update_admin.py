#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for å oppdatere admin-brukerens passord i NotatWeb-databasen
"""

import sys
import os
sys.path.append('app')

from app import app, db, Bruker
from werkzeug.security import generate_password_hash

def oppdater_admin():
    with app.app_context():
        # Finn admin-bruker
        admin = Bruker.query.filter_by(brukernavn='admin').first()
        if not admin:
            print("Admin-bruker finnes ikke!")
            return
        
        # Oppdater admin-brukerens passord
        admin.passord_hash = generate_password_hash('admin123')
        admin.er_admin = True  # Sikre at admin-flagget er satt
        db.session.commit()
        
        print("Admin-bruker oppdatert!")
        print("Brukernavn: admin")
        print("Passord: admin123")

if __name__ == '__main__':
    oppdater_admin()
