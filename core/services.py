from flask import session
from flask_login import current_user

from core.models import Goal, NutritionPlan, PhysicalProfile, MealSuggestion, ProgressCheckIn
from datetime import date


def get_current_profile():
    return (
        PhysicalProfile.query.filter_by(user_id=current_user.id)
        .order_by(PhysicalProfile.created_at.desc())
        .first()
    )


def get_current_goal():
    return (
        Goal.query.filter_by(user_id=current_user.id, is_active=True)
        .order_by(Goal.created_at.desc())
        .first()
    )


def get_current_plan():
    return (
        NutritionPlan.query.filter_by(user_id=current_user.id)
        .order_by(NutritionPlan.created_at.desc())
        .first()
    )


def plan_to_template(plan):
    if not plan:
        return None
    return {
        "nome": plan.name,
        "calorias": plan.calories,
        "proteina": plan.protein,
        "carboidratos": plan.carbs,
        "gordura": plan.fat,
    }


def clear_generated_meals():
    session.pop("refeicoes", None)


def calcular_streak(user_id):
    dates = []
    meals = MealSuggestion.query.filter_by(user_id=user_id).all()
    check_ins = ProgressCheckIn.query.filter_by(user_id=user_id).all()

    for meal in meals:
        dates.append(meal.created_at.date())
    for check in check_ins:
        dates.append(check.created_at.date())

    unique_dates = sorted(set(dates), reverse=True)

    if not unique_dates:
        return 0
    if unique_dates[0] != date.today():
        return 0

    streak = 1
    for i in range(len(unique_dates) - 1):
        diff = (unique_dates[i] - unique_dates[i + 1]).days
        if diff == 1:
            streak += 1
        else:
            break
    return streak