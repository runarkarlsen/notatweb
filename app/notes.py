from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Notat, Bruker
import logging

# Blueprint for notatrelaterte ruter
notes_bp = Blueprint('notes', __name__)
logger = logging.getLogger(__name__)

@notes_bp.route('/debug', methods=['GET'])
@jwt_required()
def debug_token():
    """
    Feilsøkingsendepunkt for å verifisere JWT-token og bruker-ID
    Krever gyldig JWT-token i Authorization-header
    """
    try:
        bruker_id = get_jwt_identity()
        bruker = Bruker.query.get(int(bruker_id))
        if bruker:
            return jsonify({
                'msg': 'Token er gyldig',
                'bruker_id': bruker_id,
                'brukernavn': bruker.brukernavn
            })
        return jsonify({'msg': 'Bruker ikke funnet', 'bruker_id': bruker_id}), 404
    except Exception as e:
        logger.error(f"Feilsøkingsendepunkt feil: {e}")
        return jsonify({'msg': 'Feil ved token-verifisering', 'error': str(e)}), 500

@notes_bp.route('/', methods=['GET'])
@jwt_required()
def hent_notater():
    """
    Hent alle notater for innlogget bruker
    Krever gyldig JWT-token i Authorization-header
    """
    try:
        bruker_id = int(get_jwt_identity())
        logger.info(f"Henter notater for bruker_id: {bruker_id}")
        notater = Notat.query.filter_by(bruker_id=bruker_id).all()
        logger.info(f"Fant {len(notater)} notater for bruker {bruker_id}")
        return jsonify([notat.to_dict() for notat in notater])
    except Exception as e:
        logger.error(f"Feil ved henting av notater: {e}")
        return jsonify({'msg': 'Kunne ikke hente notater'}), 500

@notes_bp.route('/', methods=['POST'])
@jwt_required()
def lagre_notat():
    """
    Opprett et nytt notat for innlogget bruker
    Krever gyldig JWT-token i Authorization-header
    Forventer JSON med 'tittel' og 'innhold'
    Admin-brukere kan ikke opprette notater
    """
    try:
        bruker_id = int(get_jwt_identity())
        bruker = Bruker.query.get(bruker_id)
        
        # Sjekk om brukeren er admin
        if bruker and bruker.er_admin:
            return jsonify({'msg': 'Admin-brukere kan ikke opprette notater'}), 403
        
        data = request.get_json()
        tittel = data.get('tittel')
        innhold = data.get('innhold')

        # Valider at både tittel og innhold er oppgitt
        if not tittel or not innhold:
            return jsonify({'msg': 'Tittel og innhold må oppgis'}), 400

        # Opprett og lagre nytt notat
        logger.info(f"Lagrer nytt notat for bruker_id: {bruker_id}")
        nytt_notat = Notat(tittel=tittel, innhold=innhold, bruker_id=bruker_id)
        db.session.add(nytt_notat)
        db.session.commit()
        logger.info(f"Notat lagret med ID: {nytt_notat.id}")

        return jsonify(nytt_notat.to_dict()), 201
    except Exception as e:
        logger.error(f"Feil ved lagring av notat: {e}")
        return jsonify({'msg': 'Kunne ikke lagre notat'}), 500

@notes_bp.route('/<int:notat_id>', methods=['PUT'])
@jwt_required()
def oppdater_notat(notat_id):
    """
    Oppdater et eksisterende notat
    Krever gyldig JWT-token i Authorization-header
    Forventer JSON med 'tittel' og/eller 'innhold'
    """
    try:
        data = request.get_json()
        bruker_id = int(get_jwt_identity())
        notat = Notat.query.filter_by(id=notat_id, bruker_id=bruker_id).first()

        # Sjekk om notatet eksisterer og tilhører brukeren
        if not notat:
            return jsonify({'msg': 'Notat ikke funnet'}), 404

        # Oppdater notatets felter
        notat.tittel = data.get('tittel', notat.tittel)
        notat.innhold = data.get('innhold', notat.innhold)
        db.session.commit()

        return jsonify(notat.to_dict())
    except Exception as e:
        logger.error(f"Feil ved oppdatering av notat: {e}")
        return jsonify({'msg': 'Kunne ikke oppdatere notat'}), 500

@notes_bp.route('/<int:notat_id>', methods=['DELETE'])
@jwt_required()
def slett_notat(notat_id):
    """
    Slett et eksisterende notat
    Krever gyldig JWT-token i Authorization-header
    """
    try:
        bruker_id = int(get_jwt_identity())
        notat = Notat.query.filter_by(id=notat_id, bruker_id=bruker_id).first()

        # Sjekk om notatet eksisterer og tilhører brukeren
        if not notat:
            return jsonify({'msg': 'Notat ikke funnet'}), 404

        # Slett notatet fra databasen
        db.session.delete(notat)
        db.session.commit()

        return jsonify({'msg': 'Notat slettet'})
    except Exception as e:
        logger.error(f"Feil ved sletting av notat: {e}")
        return jsonify({'msg': 'Kunne ikke slette notat'}), 500
