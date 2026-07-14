from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from core.models import db
from core.services import get_or_create_daily_tracker
from flask import render_template
from datetime import date, timedelta
from core.models import DailyTracker

tracker_bp = Blueprint("tracker", __name__)


@tracker_bp.route("/tracker/agua", methods=["POST"])
@login_required
def atualizar_agua():
    data = request.get_json() or {}

    if "agua_ml" not in data:
        return jsonify({"erro": "Campo 'agua_ml' e obrigatorio."}), 400

    try:
        agua_ml = int(data["agua_ml"])
    except (ValueError, TypeError):
        return jsonify({"erro": "Valor de agua invalido."}), 400

    if agua_ml < 0:
        return jsonify({"erro": "O valor de agua nao pode ser negativo."}), 400

    tracker = get_or_create_daily_tracker(current_user.id)
    tracker.water_ml = agua_ml
    db.session.commit()

    return jsonify({"agua_ml": tracker.water_ml}), 200


@tracker_bp.route("/tracker/sono", methods=["POST"])
@login_required
def atualizar_sono():
    data = request.get_json() or {}

    if "sono_horas" not in data:
        return jsonify({"erro": "Campo 'sono_horas' e obrigatorio."}), 400

    try:
        sono_horas = float(data["sono_horas"])
    except (ValueError, TypeError):
        return jsonify({"erro": "Valor de sono invalido."}), 400

    if sono_horas < 0 or sono_horas > 24:
        return jsonify({"erro": "Horas de sono devem estar entre 0 e 24."}), 400

    tracker = get_or_create_daily_tracker(current_user.id)
    tracker.sleep_hours = sono_horas
    db.session.commit()

    return jsonify({"sono_horas": tracker.sleep_hours}), 200

@tracker_bp.route("/metricas")
@login_required
def metricas():
    hoje = date.today()

    registros = (
        DailyTracker.query.filter_by(user_id=current_user.id)
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

    medias = {
        "agua": {
            "diaria": media(1, "water_ml"),
            "semanal": media(7, "water_ml"),
            "mensal": media(30, "water_ml"),
        },
        "sono": {
            "diaria": media(1, "sleep_hours"),
            "semanal": media(7, "sleep_hours"),
            "mensal": media(30, "sleep_hours"),
        },
    }

    return render_template("metricas.html", registros=registros, medias=medias)
