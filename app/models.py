from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Bruker(db.Model):
    """
    Brukermodell for å lagre brukerinformasjon
    """
    id = db.Column(db.Integer, primary_key=True)
    brukernavn = db.Column(db.String(80), unique=True, nullable=False)
    passord_hash = db.Column(db.String(120), nullable=False)
    er_admin = db.Column(db.Boolean, default=False)
    opprettet = db.Column(db.DateTime, default=datetime.utcnow)
    notater = db.relationship('Notat', backref='bruker', lazy=True, cascade='all, delete-orphan')

    def sett_passord(self, passord):
        """Krypterer og lagrer passordet"""
        self.passord_hash = generate_password_hash(passord)

    def sjekk_passord(self, passord):
        """Sjekker om passordet er korrekt"""
        return check_password_hash(self.passord_hash, passord)

    def to_dict(self):
        """Konverterer bruker til dictionary"""
        return {
            'id': self.id,
            'brukernavn': self.brukernavn,
            'er_admin': self.er_admin,
            'opprettet': self.opprettet.isoformat()
        }

class Notat(db.Model):
    """
    Notatmodell for å lagre brukernotater
    """
    id = db.Column(db.Integer, primary_key=True)
    tittel = db.Column(db.String(100), nullable=False)
    innhold = db.Column(db.Text, nullable=False)
    opprettet = db.Column(db.DateTime, default=datetime.utcnow)
    bruker_id = db.Column(db.Integer, db.ForeignKey('bruker.id'), nullable=False)

    def to_dict(self):
        """Konverterer notat til dictionary"""
        return {
            'id': self.id,
            'tittel': self.tittel,
            'innhold': self.innhold,
            'opprettet': self.opprettet.isoformat(),
            'bruker_id': self.bruker_id
        }
