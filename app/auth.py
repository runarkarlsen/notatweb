from flask import Blueprint, request, jsonify
from models import db, Bruker
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

# Blueprint for autentiseringsrelaterte ruter
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Registrer en ny bruker i systemet
    Forventer JSON med 'brukernavn' og 'passord'
    """
    data = request.get_json()
    brukernavn = data.get('brukernavn')
    passord = data.get('passord')

    # Valider at både brukernavn og passord er oppgitt
    if not brukernavn or not passord:
        return jsonify({'msg': 'Brukernavn og passord må oppgis'}), 400

    # Sjekk om brukernavnet allerede eksisterer
    if Bruker.query.filter_by(brukernavn=brukernavn).first():
        return jsonify({'msg': 'Brukernavn er allerede tatt'}), 409

    # Opprett ny bruker med kryptert passord
    ny_bruker = Bruker(brukernavn=brukernavn)
    ny_bruker.sett_passord(passord)
    db.session.add(ny_bruker)
    db.session.commit()

    return jsonify({'msg': 'Bruker opprettet'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Logg inn en eksisterende bruker
    Forventer JSON med 'brukernavn' og 'passord'
    Returnerer JWT-token ved vellykket innlogging
    """
    data = request.get_json()
    brukernavn = data.get('brukernavn')
    passord = data.get('passord')

    # Valider at både brukernavn og passord er oppgitt
    if not brukernavn or not passord:
        return jsonify({'msg': 'Brukernavn og passord må oppgis'}), 400

    # Finn bruker i databasen
    bruker = Bruker.query.filter_by(brukernavn=brukernavn).first()

    # Sjekk om bruker eksisterer og passord er korrekt
    if not bruker or not bruker.sjekk_passord(passord):
        return jsonify({'msg': 'Ugyldig brukernavn eller passord'}), 401

    # Opprett JWT-token som utløper etter 1 time
    access_token = create_access_token(identity=str(bruker.id), expires_delta=timedelta(hours=1))
    return jsonify({'access_token': access_token, 'bruker': bruker.to_dict()})

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Endre passord for innlogget bruker
    Forventer JSON med 'gammelt_passord' og 'nytt_passord'
    """
    data = request.get_json()
    gammelt_passord = data.get('gammelt_passord')
    nytt_passord = data.get('nytt_passord')

    # Valider at både gammelt og nytt passord er oppgitt
    if not gammelt_passord or not nytt_passord:
        return jsonify({'msg': 'Både gammelt og nytt passord må oppgis'}), 400

    # Hent innlogget bruker
    bruker_id = get_jwt_identity()
    bruker = Bruker.query.get(bruker_id)

    if not bruker:
        return jsonify({'msg': 'Bruker ikke funnet'}), 404

    # Verifiser gammelt passord
    if not bruker.sjekk_passord(gammelt_passord):
        return jsonify({'msg': 'Feil gammelt passord'}), 401

    # Oppdater til nytt passord
    bruker.sett_passord(nytt_passord)
    db.session.commit()

    return jsonify({'msg': 'Passord endret'}), 200
