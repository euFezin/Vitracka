from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from core.models import Goal, PhysicalProfile, NutritionPlan, db
from core.cenarios import gerar_cenarios
from core.services import get_current_profile, get_current_goal, clear_generated_meals

api_onboarding_bp = Blueprint("api_onboarding", __name__, url_prefix="/api")


@api_onboarding_bp.route("/onboarding/objetivo", methods=["POST"])
@jwt_required()
def api_onboarding_objetivo():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    objective = data.get("objetivo")
    target_weight = data.get("peso_alvo")

    if not objective or not target_weight:
        return jsonify({"erro": "Objetivo e peso alvo sao obrigatorios."}), 400

    Goal.query.filter_by(user_id=user_id, is_active=True).update({"is_active": False})

    goal = Goal(
        user_id=user_id,
        objective=objective,
        target_weight=float(target_weight),
        is_active=True,
    )
    db.session.add(goal)
    db.session.commit()

    return jsonify({"ok": True}), 201


@api_onboarding_bp.route("/onboarding/perfil", methods=["POST"])
@jwt_required()
def api_onboarding_perfil():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    try:
        gender = data["genero"]
        weight = float(data["peso"])
        height = float(data["altura"])
        age = int(data["idade"])
        activity_level = data["atividade"]
    except (KeyError, ValueError, TypeError):
        return jsonify({"erro": "Dados fisicos invalidos ou incompletos."}), 400

    profile = PhysicalProfile(
        user_id=user_id,
        gender=gender,
        weight=weight,
        height=height,
        age=age,
        activity_level=activity_level,
    )
    db.session.add(profile)
    db.session.commit()

    return jsonify({"ok": True}), 201


@api_onboarding_bp.route("/onboarding/cenarios", methods=["GET"])
@jwt_required()
def api_onboarding_cenarios():
    user_id = int(get_jwt_identity())

    profile = get_current_profile(user_id)
    goal = get_current_goal(user_id)

    if not profile or not goal or not profile.activity_level:
        return jsonify({"erro": "Complete o objetivo e o perfil fisico antes."}), 400

    gender = profile.gender
    weight = profile.weight
    height = profile.height
    age = profile.age
    objective = goal.objective
    activity = profile.activity_level

    if gender == "masculino":
        tmb = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        tmb = 10 * weight + 6.25 * height - 5 * age - 161

    factors = {
        "sedentario": 1.2,
        "leve": 1.375,
        "moderado": 1.55,
        "intenso": 1.725,
    }

    tdee = tmb * factors.get(activity, 1.2)
    scenarios = gerar_cenarios(tdee, weight, objective)

    for scenario in scenarios:
        calories = scenario["calorias"]
        protein = weight * scenario["fator_proteina"]
        fat = weight * scenario["fator_gordura"]
        carbs = (calories - (protein * 4 + fat * 9)) / 4

        scenario["proteina"] = round(protein)
        scenario["gordura"] = round(fat)
        scenario["carboidratos"] = round(carbs)
        scenario["calorias"] = round(calories)

    return jsonify({"cenarios": scenarios}), 200


@api_onboarding_bp.route("/onboarding/plano", methods=["POST"])
@jwt_required()
def api_onboarding_selecionar_plano():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    try:
        nome = data["nome"]
        calorias = int(data["calorias"])
        proteina = int(data["proteina"])
        carboidratos = int(data["carboidratos"])
        gordura = int(data["gordura"])
    except (KeyError, ValueError, TypeError):
        return jsonify({"erro": "Dados do plano invalidos ou incompletos."}), 400

    clear_generated_meals()

    plan = NutritionPlan(
        user_id=user_id,
        name=nome,
        calories=calorias,
        protein=proteina,
        carbs=carboidratos,
        fat=gordura,
    )
    db.session.add(plan)
    db.session.commit()

    return jsonify({"ok": True, "plano": {
        "nome": plan.name,
        "calorias": plan.calories,
        "proteina": plan.protein,
        "carboidratos": plan.carbs,
        "gordura": plan.fat,
    }}), 201