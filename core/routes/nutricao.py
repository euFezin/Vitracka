import json

from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_required, current_user

from core.models import MealSuggestion, db
from core.ia_explicacao import gerar_explicacao
from core.refeicoes import gerar_refeicao, gerar_todas_refeicoes
from core.services import get_current_plan, get_current_profile, get_current_goal, plan_to_template

nutricao_bp = Blueprint("nutricao", __name__)


@nutricao_bp.route("/explicacao")
@login_required
def explicacao():
    plan = get_current_plan()
    profile = get_current_profile()

    if not plan:
        return redirect(url_for("dashboard.dashboard"))

    template_plan = plan_to_template(plan)
    goal = get_current_goal()

    texto_ia = gerar_explicacao(
        plano=template_plan["nome"],
        objetivo=goal.objective if goal else None,
        peso=profile.weight if profile else None,
        atividade=profile.activity_level if profile else None,
    )

    return render_template("explicacao.html", plano=template_plan, texto_ia=texto_ia)


@nutricao_bp.route("/refeicoes")
@login_required
def refeicoes():
    plan = get_current_plan()

    if not plan:
        return redirect(url_for("dashboard.dashboard"))

    template_plan = plan_to_template(plan)

    if "refeicoes" not in session:
        saved_meals = (
            MealSuggestion.query.filter_by(user_id=current_user.id, nutrition_plan_id=plan.id)
            .order_by(MealSuggestion.created_at.desc())
            .first()
        )

        if saved_meals:
            session["refeicoes"] = json.loads(saved_meals.meals_json)
        else:
            session["refeicoes"] = gerar_todas_refeicoes(template_plan)
            db.session.add(
                MealSuggestion(
                    user_id=current_user.id,
                    nutrition_plan_id=plan.id,
                    meals_json=json.dumps(session["refeicoes"], ensure_ascii=False),
                )
            )
            db.session.commit()

        session.modified = True

    return render_template("refeicoes.html", plano=template_plan, refeicoes=session["refeicoes"])


@nutricao_bp.route("/regenerar-refeicao", methods=["POST"])
@login_required
def regenerar_refeicao():
    plan = get_current_plan()

    if not plan:
        return redirect(url_for("dashboard.dashboard"))

    meal_name = request.form["refeicao"]
    template_plan = plan_to_template(plan)
    meals = session.get("refeicoes", {})
    nova = gerar_refeicao(meal_name, template_plan)

    print("==========")
    print("Refeição:", meal_name)
    print("Resposta:", repr(nova))
    print("==========")

    if nova.strip():
        meals[meal_name] = nova
        session["refeicoes"] = meals
        session.modified = True

        saved_meals = (
            MealSuggestion.query.filter_by(
                user_id=current_user.id,
                nutrition_plan_id=plan.id
            )
            .order_by(MealSuggestion.created_at.desc())
            .first()
        )

        if saved_meals:
            saved_meals.meals_json = json.dumps(meals, ensure_ascii=False)
            db.session.commit()

    return redirect(url_for("nutricao.refeicoes"))