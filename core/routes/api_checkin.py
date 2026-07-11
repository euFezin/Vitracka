from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from core.models import ProgressCheckIn, db

api_checkin_bp = Blueprint("api_checkin", __name__, url_prefix="/api")


@api_checkin_bp.route("/checkins", methods=["GET"])
@jwt_required()
def api_listar_checkins():
    user_id = int(get_jwt_identity())

    checkins = (
        ProgressCheckIn.query.filter_by(user_id=user_id)
        .order_by(ProgressCheckIn.created_at.desc())
        .limit(20)
        .all()
    )

    return jsonify({
        "checkins": [
            {
                "id": c.id,
                "peso": c.weight,
                "cintura": c.waist,
                "observacoes": c.notes,
                "data": c.created_at.isoformat(),
            }
            for c in checkins
        ]
    }), 200


@api_checkin_bp.route("/checkins", methods=["POST"])
@jwt_required()
def api_criar_checkin():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or "peso" not in data:
        return jsonify({"erro": "Campo 'peso' e obrigatorio."}), 400

    try:
        peso = float(data["peso"])
        cintura = float(data["cintura"]) if data.get("cintura") else None
    except (ValueError, TypeError):
        return jsonify({"erro": "Peso ou cintura invalidos."}), 400

    checkin = ProgressCheckIn(
        user_id=user_id,
        weight=peso,
        waist=cintura,
        notes=data.get("observacoes") or None,
    )
    db.session.add(checkin)
    db.session.commit()

    return jsonify({
        "id": checkin.id,
        "peso": checkin.weight,
        "cintura": checkin.waist,
        "observacoes": checkin.notes,
        "data": checkin.created_at.isoformat(),
    }), 201