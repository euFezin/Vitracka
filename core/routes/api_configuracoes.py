from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from core.models import User, PhysicalProfile, Goal, MealSuggestion, NutritionPlan, ProgressCheckIn, WorkoutPlan, db
from core.services import get_current_profile, get_current_goal

api_configuracoes_bp = Blueprint("api_configuracoes", __name__, url_prefix="/api")


@api_configuracoes_bp.route("/configuracoes", methods=["GET"])
@jwt_required()
def api_configuracoes():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    profile = get_current_profile(user_id)
    goal = get_current_goal(user_id)

    return jsonify({
        "usuario": {"nome": user.name, "email": user.email},
        "perfil": {
            "genero": profile.gender,
            "peso": profile.weight,
            "altura": profile.height,
            "idade": profile.age,
            "atividade": profile.activity_level,
        } if profile else None,
        "objetivo": {
            "tipo": goal.objective,
            "peso_alvo": goal.target_weight,
        } if goal else None,
    }), 200


@api_configuracoes_bp.route("/configuracoes/perfil", methods=["PUT"])
@jwt_required()
def api_configuracoes_perfil():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    nome = data.get("nome", "").strip()
    email = data.get("email", "").strip().lower()

    if not nome or not email:
        return jsonify({"erro": "Preencha nome e email."}), 400

    email_em_uso = User.query.filter(User.email == email, User.id != user_id).first()
    if email_em_uso:
        return jsonify({"erro": "Esse email ja esta em uso por outra conta."}), 409

    user = db.session.get(User, user_id)
    user.name = nome
    user.email = email
    db.session.commit()

    return jsonify({"ok": True, "nome": user.name, "email": user.email}), 200


@api_configuracoes_bp.route("/configuracoes/senha", methods=["PUT"])
@jwt_required()
def api_configuracoes_senha():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    senha_atual = data.get("senha_atual", "")
    nova_senha = data.get("nova_senha", "")
    confirmar_senha = data.get("confirmar_senha", "")

    user = db.session.get(User, user_id)

    if not user.check_password(senha_atual):
        return jsonify({"erro": "Senha atual incorreta."}), 401

    if len(nova_senha) < 6:
        return jsonify({"erro": "A nova senha deve ter pelo menos 6 caracteres."}), 400

    if nova_senha != confirmar_senha:
        return jsonify({"erro": "As senhas nao coincidem."}), 400

    user.set_password(nova_senha)
    db.session.commit()

    return jsonify({"ok": True}), 200


@api_configuracoes_bp.route("/configuracoes/fisico", methods=["PUT"])
@jwt_required()
def api_configuracoes_fisico():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    try:
        gender = data.get("genero")
        weight = float(data["peso"])
        height = float(data["altura"])
        age = int(data["idade"])
        activity_level = data.get("atividade")
        objective = data.get("objetivo")
        target_weight = data.get("target_weight")
    except (KeyError, ValueError, TypeError):
        return jsonify({"erro": "Dados fisicos invalidos ou incompletos."}), 400

    db.session.add(
        PhysicalProfile(
            user_id=user_id,
            gender=gender,
            weight=weight,
            height=height,
            age=age,
            activity_level=activity_level or None,
        )
    )

    if objective:
        Goal.query.filter_by(user_id=user_id, is_active=True).update({"is_active": False})
        db.session.add(
            Goal(
                user_id=user_id,
                objective=objective,
                target_weight=float(target_weight) if target_weight else None,
                is_active=True,
            )
        )

    db.session.commit()
    return jsonify({"ok": True}), 200


@api_configuracoes_bp.route("/configuracoes/excluir-conta", methods=["POST"])
@jwt_required()
def api_excluir_conta():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    senha = data.get("senha", "")

    user = db.session.get(User, user_id)

    if not user.check_password(senha):
        return jsonify({"erro": "Senha incorreta. Sua conta nao foi excluida."}), 401

    MealSuggestion.query.filter_by(user_id=user_id).delete()
    NutritionPlan.query.filter_by(user_id=user_id).delete()
    ProgressCheckIn.query.filter_by(user_id=user_id).delete()
    WorkoutPlan.query.filter_by(user_id=user_id).delete()
    Goal.query.filter_by(user_id=user_id).delete()
    PhysicalProfile.query.filter_by(user_id=user_id).delete()

    db.session.delete(user)
    db.session.commit()

    return jsonify({"ok": True}), 200