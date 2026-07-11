from flask import session
from flask_login import current_user

from core.models import Goal, NutritionPlan, PhysicalProfile, MealSuggestion, ProgressCheckIn, WorkoutPlan
from datetime import date


def get_current_profile(user_id=None):
    uid = user_id if user_id is not None else current_user.id
    return (
        PhysicalProfile.query.filter_by(user_id=uid)
        .order_by(PhysicalProfile.created_at.desc())
        .first()
    )


def get_current_goal(user_id=None):
    uid = user_id if user_id is not None else current_user.id
    return (
        Goal.query.filter_by(user_id=uid, is_active=True)
        .order_by(Goal.created_at.desc())
        .first()
    )


def get_current_plan(user_id=None):
    uid = user_id if user_id is not None else current_user.id
    return (
        NutritionPlan.query.filter_by(user_id=uid)
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

def montar_dados_dashboard(user_id):
    profile = (
        PhysicalProfile.query.filter_by(user_id=user_id)
        .order_by(PhysicalProfile.created_at.asc())
        .first()
    )
    goal = (
        Goal.query.filter_by(user_id=user_id, is_active=True)
        .order_by(Goal.created_at.desc())
        .first()
    )
    plan = (
        NutritionPlan.query.filter_by(user_id=user_id)
        .order_by(NutritionPlan.created_at.desc())
        .first()
    )
    check_ins = (
        ProgressCheckIn.query.filter_by(user_id=user_id)
        .order_by(ProgressCheckIn.created_at.desc())
        .limit(5)
        .all()
    )
    latest_meal = (
        MealSuggestion.query.filter_by(user_id=user_id)
        .order_by(MealSuggestion.created_at.desc())
        .first()
    )
    latest_check_in = (
        ProgressCheckIn.query.filter_by(user_id=user_id)
        .order_by(ProgressCheckIn.created_at.desc())
        .first()
    )
    workout = WorkoutPlan.query.filter_by(user_id=user_id).first()

    current_weight = None
    if latest_check_in:
        current_weight = latest_check_in.weight
    elif profile:
        current_weight = profile.weight

    progress = 0
    remaining_weight = 0

    if goal and goal.target_weight and profile and current_weight:
        initial_weight = profile.weight
        target_weight = goal.target_weight

        if initial_weight != target_weight:
            if goal.objective == "cutting":
                progress = (
                    (initial_weight - current_weight) /
                    (initial_weight - target_weight)
                ) * 100
                remaining_weight = current_weight - target_weight
            elif goal.objective == "bulking":
                progress = (
                    (current_weight - initial_weight) /
                    (target_weight - initial_weight)
                ) * 100
                remaining_weight = target_weight - current_weight

        progress = max(0, min(progress, 100))

    streak = calcular_streak(user_id)

    return {
        "profile": profile,
        "goal": goal,
        "plan": plan,
        "check_ins": check_ins,
        "latest_meal": latest_meal,
        "workout": workout,
        "current_weight": current_weight,
        "progress": progress,
        "remaining_weight": remaining_weight,
        "streak": streak,
    }