from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from core.models import WorkoutPlan, db
from core.workout import gerar_treino
from core.services import get_current_profile, get_current_goal

api_treino_bp = Blueprint("api_treino", __name__, url_prefix="/api")


@api_treino_bp.route("/treino", methods=["GET"])
@jwt_required()
def api_treino():
    user_id = int(get_jwt_identity())

    workout = WorkoutPlan.query.filter_by(user_id=user_id).first()

    if not workout:
        return jsonify({"erro": "Nenhum treino encontrado."}), 404

    return jsonify({
        "conteudo": workout.content,
        "atualizado_em": workout.updated_at.isoformat(),
    }), 200


@api_treino_bp.route("/treino/gerar", methods=["POST"])
@jwt_required()
def api_gerar_treino():
    user_id = int(get_jwt_identity())

    profile = get_current_profile(user_id)
    goal = get_current_goal(user_id)

    if not profile or not goal:
        return jsonify({"erro": "Perfil ou objetivo nao configurados."}), 400

    treino_gerado = gerar_treino(profile, goal)

    workout = WorkoutPlan.query.filter_by(user_id=user_id).first()

    if workout:
        workout.content = treino_gerado
    else:
        workout = WorkoutPlan(user_id=user_id, content=treino_gerado)
        db.session.add(workout)

    db.session.commit()

    return jsonify({"conteudo": workout.content}), 200