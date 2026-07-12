from datetime import date, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from core.models import DailyTracker, db

api_tracker_bp = Blueprint("api_tracker", __name__, url_prefix="/api")


def _get_or_create_hoje(user_id):
    hoje = date.today()
    tracker = DailyTracker.query.filter_by(user_id=user_id, date=hoje).first()

    if not tracker:
        tracker = DailyTracker(user_id=user_id, date=hoje, water_ml=0, steps=0, sleep_hours=None)
        db.session.add(tracker)
        db.session.commit()

    return tracker


@api_tracker_bp.route("/tracker/hoje", methods=["GET"])
@jwt_required()
def api_tracker_hoje():
    user_id = int(get_jwt_identity())
    tracker = _get_or_create_hoje(user_id)

    return jsonify({
        "data": tracker.date.isoformat(),
        "agua_ml": tracker.water_ml,
        "sono_horas": tracker.sleep_hours,
    }), 200


@api_tracker_bp.route("/tracker/agua", methods=["PUT"])
@jwt_required()
def api_tracker_agua():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    if "agua_ml" not in data:
        return jsonify({"erro": "Campo 'agua_ml' e obrigatorio."}), 400

    try:
        agua_ml = int(data["agua_ml"])
    except (ValueError, TypeError):
        return jsonify({"erro": "Valor de agua invalido."}), 400

    if agua_ml < 0:
        return jsonify({"erro": "O valor de agua nao pode ser negativo."}), 400

    tracker = _get_or_create_hoje(user_id)
    tracker.water_ml = agua_ml
    db.session.commit()

    return jsonify({"agua_ml": tracker.water_ml}), 200


@api_tracker_bp.route("/tracker/sono", methods=["PUT"])
@jwt_required()
def api_tracker_sono():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    if "sono_horas" not in data:
        return jsonify({"erro": "Campo 'sono_horas' e obrigatorio."}), 400

    try:
        sono_horas = float(data["sono_horas"])
    except (ValueError, TypeError):
        return jsonify({"erro": "Valor de sono invalido."}), 400

    if sono_horas < 0 or sono_horas > 24:
        return jsonify({"erro": "Horas de sono devem estar entre 0 e 24."}), 400

    tracker = _get_or_create_hoje(user_id)
    tracker.sleep_hours = sono_horas
    db.session.commit()

    return jsonify({"sono_horas": tracker.sleep_hours}), 200

@api_tracker_bp.route("/tracker/historico", methods=["GET"])
@jwt_required()
def api_tracker_historico():
    user_id = int(get_jwt_identity())
    hoje = date.today()

    registros = (
        DailyTracker.query.filter_by(user_id=user_id)
        .order_by(DailyTracker.date.desc())
        .limit(30)
        .all()
    )

    def media(dias, campo):
        limite = hoje - timedelta(days=dias)
        valores = [getattr(r, campo) for r in registros if r.date > limite and getattr(r, campo) is not None]
        if not valores:
            return None
        return round(sum(valores) / len(valores), 1)

    return jsonify({
        "historico": [
            {
                "data": r.date.isoformat(),
                "agua_ml": r.water_ml,
                "sono_horas": r.sleep_hours,
            }
            for r in registros
        ],
        "medias": {
            "agua_ml": {
                "diaria": media(1, "water_ml"),
                "semanal": media(7, "water_ml"),
                "mensal": media(30, "water_ml"),
            },
            "sono_horas": {
                "diaria": media(1, "sleep_hours"),
                "semanal": media(7, "sleep_hours"),
                "mensal": media(30, "sleep_hours"),
            },
        },
    }), 200