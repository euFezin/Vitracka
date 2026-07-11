import json

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from core.models import MealSuggestion, db
from core.refeicoes import gerar_todas_refeicoes, gerar_refeicao
from core.services import get_current_plan, plan_to_template
from core.ia_explicacao import gerar_explicacao
from core.services import get_current_profile, get_current_goal

api_nutricao_bp = Blueprint("api_nutricao", __name__, url_prefix="/api")


@api_nutricao_bp.route("/refeicoes", methods=["GET"])
@jwt_required()
def api_refeicoes():
    user_id = int(get_jwt_identity())
    plan = get_current_plan(user_id)

    if not plan:
        return jsonify({"erro": "Nenhum plano alimentar encontrado."}), 404

    template_plan = plan_to_template(plan)

    saved_meals = (
        MealSuggestion.query.filter_by(user_id=user_id, nutrition_plan_id=plan.id)
        .order_by(MealSuggestion.created_at.desc())
        .first()
    )

    if saved_meals:
        refeicoes = json.loads(saved_meals.meals_json)
    else:
        refeicoes = gerar_todas_refeicoes(template_plan)
        db.session.add(
            MealSuggestion(
                user_id=user_id,
                nutrition_plan_id=plan.id,
                meals_json=json.dumps(refeicoes, ensure_ascii=False),
            )
        )
        db.session.commit()

    return jsonify({
        "plano": template_plan,
        "refeicoes": refeicoes,
    }), 200


@api_nutricao_bp.route("/refeicoes/regenerar", methods=["POST"])
@jwt_required()
def api_regenerar_refeicao():
    from flask import request

    user_id = int(get_jwt_identity())
    plan = get_current_plan(user_id)

    if not plan:
        return jsonify({"erro": "Nenhum plano alimentar encontrado."}), 404

    data = request.get_json()
    if not data or "refeicao" not in data:
        return jsonify({"erro": "Campo 'refeicao' e obrigatorio."}), 400

    meal_name = data["refeicao"]
    template_plan = plan_to_template(plan)
    nova = gerar_refeicao(meal_name, template_plan)

    if not nova.strip():
        return jsonify({"erro": "Nao foi possivel gerar a refeicao."}), 500

    saved_meals = (
        MealSuggestion.query.filter_by(user_id=user_id, nutrition_plan_id=plan.id)
        .order_by(MealSuggestion.created_at.desc())
        .first()
    )

    if saved_meals:
        meals = json.loads(saved_meals.meals_json)
        meals[meal_name] = nova
        saved_meals.meals_json = json.dumps(meals, ensure_ascii=False)
        db.session.commit()
    else:
        meals = {meal_name: nova}

    return jsonify({"refeicao": meal_name, "conteudo": nova}), 200

@api_nutricao_bp.route("/explicacao", methods=["GET"])
@jwt_required()
def api_explicacao():
    user_id = int(get_jwt_identity())

    plan = get_current_plan(user_id)
    profile = get_current_profile(user_id)
    goal = get_current_goal(user_id)

    if not plan:
        return jsonify({"erro": "Nenhum plano alimentar encontrado."}), 404

    template_plan = plan_to_template(plan)

    texto_ia = gerar_explicacao(
        plano=template_plan["nome"],
        objetivo=goal.objective if goal else None,
        peso=profile.weight if profile else None,
        atividade=profile.activity_level if profile else None,
    )

    return jsonify({
        "plano": template_plan,
        "explicacao": texto_ia,
    }), 200