from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from core.services import montar_dados_dashboard

api_dashboard_bp = Blueprint("api_dashboard", __name__, url_prefix="/api")


@api_dashboard_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def api_dashboard():
    user_id = int(get_jwt_identity())
    dados = montar_dados_dashboard(user_id)

    return jsonify({
        "perfil": {
            "peso": dados["profile"].weight if dados["profile"] else None,
            "altura": dados["profile"].height if dados["profile"] else None,
        } if dados["profile"] else None,
        "objetivo": dados["goal"].objective if dados["goal"] else None,
        "peso_atual": dados["current_weight"],
        "progresso": round(dados["progress"], 1),
        "peso_restante": dados["remaining_weight"],
        "streak": dados["streak"],
        "plano": {
            "nome": dados["plan"].name,
            "calorias": dados["plan"].calories,
            "proteina": dados["plan"].protein,
            "carboidratos": dados["plan"].carbs,
            "gordura": dados["plan"].fat,
        } if dados["plan"] else None,
    }), 200