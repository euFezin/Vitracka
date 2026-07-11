from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_required, current_user

from core.models import Goal, PhysicalProfile, db
from core.cenarios import gerar_cenarios
from core.services import get_current_profile, get_current_goal

onboarding_bp = Blueprint("onboarding", __name__)


@onboarding_bp.route("/objetivo", methods=["GET", "POST"])
@login_required
def objetivo():
    if request.method == "POST":
        objective = request.form.get("objective")
        target_weight = request.form.get("target_weight")

        new_goal = Goal(
            user_id=current_user.id,
            objective=objective,
            target_weight=float(target_weight),
            is_active=True
        )
        db.session.add(new_goal)
        db.session.commit()
        return redirect(url_for("dashboard.dashboard"))

    return render_template("objetivo.html")


@onboarding_bp.route("/salvar-objetivo", methods=["POST"])
@login_required
def salvar_objetivo():
    objective = request.form["objetivo"]
    target_weight = request.form["target_weight"]
    session["objetivo"] = objective

    Goal.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).update({
        "is_active": False
    })

    db.session.add(
        Goal(
            user_id=current_user.id,
            objective=objective,
            target_weight=float(target_weight)
        )
    )
    db.session.commit()
    return redirect(url_for("onboarding.dados"))


@onboarding_bp.route("/dados", methods=["GET", "POST"])
@login_required
def dados():
    goal = get_current_goal()

    if request.method == "POST":
        gender = request.form["genero"]
        weight = float(request.form["peso"])
        height = float(request.form["altura"])
        age = int(request.form["idade"])

        session["genero"] = gender
        session["peso"] = weight
        session["altura"] = height
        session["idade"] = age

        db.session.add(
            PhysicalProfile(
                user_id=current_user.id,
                gender=gender,
                weight=weight,
                height=height,
                age=age,
            )
        )
        db.session.commit()
        return redirect(url_for("onboarding.atividade"))

    return render_template("dados.html", objetivo=goal.objective if goal else None)


@onboarding_bp.route("/atividade", methods=["GET", "POST"])
@login_required
def atividade():
    if request.method == "POST":
        activity_level = request.form["atividade"]
        session["atividade"] = activity_level

        profile = get_current_profile()
        if profile:
            profile.activity_level = activity_level
            db.session.commit()

        return redirect(url_for("onboarding.calcular"))

    return render_template("atividade.html")


@onboarding_bp.route("/calcular")
@login_required
def calcular():
    profile = get_current_profile()
    goal = get_current_goal()

    if not profile or not goal or not profile.activity_level:
        return redirect(url_for("onboarding.objetivo"))

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

    return render_template("resultado.html", cenarios=scenarios)


@onboarding_bp.route("/selecionar-plano", methods=["POST"])
@login_required
def selecionar_plano():
    from core.models import NutritionPlan
    from core.services import clear_generated_meals

    clear_generated_meals()

    plan = NutritionPlan(
        user_id=current_user.id,
        name=request.form["nome"],
        calories=int(request.form["calorias"]),
        protein=int(request.form["proteina"]),
        carbs=int(request.form["carboidratos"]),
        fat=int(request.form["gordura"]),
    )
    db.session.add(plan)
    db.session.commit()

    session["plano_nome"] = plan.name
    session["plano_calorias"] = plan.calories
    session["plano_proteina"] = plan.protein
    session["plano_carboidratos"] = plan.carbs
    session["plano_gordura"] = plan.fat

    return redirect(url_for("nutricao.explicacao"))