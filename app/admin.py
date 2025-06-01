from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Bruker, Notat

# Blueprint for admin-relaterte ruter
admin_bp = Blueprint('admin', __name__)

def admin_required(func):
    """
    Dekorator som krever admin-tilgang for å utføre funksjonen
    Sjekker at brukeren er innlogget og har admin-rettigheter
    """
    @jwt_required()
    def wrapper(*args, **kwargs):
        bruker_id = get_jwt_identity()
        bruker = Bruker.query.get(bruker_id)
        if not bruker or not bruker.er_admin:
            return jsonify({'msg': 'Admin-tilgang kreves'}), 403
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@admin_bp.route('/brukere', methods=['GET'])
@admin_required
def hent_brukere():
    """
    Hent alle brukere i systemet med deres notater, unntatt den innloggede admin-brukeren
    Kun tilgjengelig for admin-brukere
    """
    current_user_id = get_jwt_identity()
    brukere = Bruker.query.filter(Bruker.id != current_user_id).all()
    result = []
    for bruker in brukere:
        # Konverter brukerdata til dictionary og inkluder notater
        bruker_data = bruker.to_dict()
        bruker_data['notater'] = [notat.to_dict() for notat in bruker.notater]
        result.append(bruker_data)
    return jsonify(result)

@admin_bp.route('/brukere/<int:bruker_id>', methods=['DELETE'])
@admin_required
def slett_bruker(bruker_id):
    """
    Slett en bruker og alle tilhørende notater
    Kun tilgjengelig for admin-brukere
    Forhindrer admin fra å slette seg selv
    """
    current_user_id = get_jwt_identity()
    if bruker_id == current_user_id:
        return jsonify({'msg': 'Admin kan ikke slette sin egen bruker'}), 403
        
    bruker = Bruker.query.get(bruker_id)
    if not bruker:
        return jsonify({'msg': 'Bruker ikke funnet'}), 404
    
    # Sletter brukeren (og alle tilhørende notater pga. cascade-konfigurasjon)
    db.session.delete(bruker)
    db.session.commit()
    
    return jsonify({'msg': 'Bruker og tilhørende notater slettet'})

@admin_bp.route('/brukere/<int:bruker_id>/change-password', methods=['POST'])
@admin_required
def admin_change_password(bruker_id):
    """
    Endre passord for en spesifikk bruker (kun tilgjengelig for admin)
    Forventer JSON med 'nytt_passord'
    """
    current_user_id = get_jwt_identity()
    
    # Forhindre admin fra å endre sitt eget passord via denne ruten
    if bruker_id == int(current_user_id):
        return jsonify({'msg': 'Admin kan ikke endre sitt eget passord via admin-ruten. Bruk /auth/change-password'}), 403
    
    data = request.get_json()
    nytt_passord = data.get('nytt_passord')
    
    if not nytt_passord:
        return jsonify({'msg': 'Nytt passord må oppgis'}), 400
    
    bruker = Bruker.query.get(bruker_id)
    if not bruker:
        return jsonify({'msg': 'Bruker ikke funnet'}), 404
    
    # Oppdater brukerens passord
    bruker.sett_passord(nytt_passord)
    db.session.commit()
    
    return jsonify({'msg': f'Passord endret for bruker {bruker.brukernavn}'}), 200
