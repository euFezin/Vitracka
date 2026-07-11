from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import date

from core.models import Goal, NutritionPlan, PhysicalProfile, ProgressCheckIn, MealSuggestion, WorkoutPlan
from core.services import calcular_streak

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    profile = (
        PhysicalProfile.query.filter_by(user_id=current_user.id)
        .order_by(PhysicalProfile.created_at.asc())
        .first()
    )
    goal = (
        Goal.query.filter_by(user_id=current_user.id, is_active=True)
        .order_by(Goal.created_at.desc())
        .first()
    )
    plan = (
        NutritionPlan.query.filter_by(user_id=current_user.id)
        .order_by(NutritionPlan.created_at.desc())
        .first()
    )
    check_ins = (
        ProgressCheckIn.query.filter_by(user_id=current_user.id)
        .order_by(ProgressCheckIn.created_at.desc())
        .limit(5)
        .all()
    )
    latest_meal = (
        MealSuggestion.query.filter_by(user_id=current_user.id)
        .order_by(MealSuggestion.created_at.desc())
        .first()
    )
    latest_check_in = (
        ProgressCheckIn.query.filter_by(user_id=current_user.id)
        .order_by(ProgressCheckIn.created_at.desc())
        .first()
    )
    workout = WorkoutPlan.query.filter_by(
        user_id=current_user.id
    ).first()

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

    streak = calcular_streak(current_user.id)

    return render_template(
        "dashboard.html",
        profile=profile,
        goal=goal,
        plan=plan,
        check_ins=check_ins,
        latest_meal=latest_meal,
        workout=workout,
        current_weight=current_weight,
        progress=progress,
        remaining_weight=remaining_weight,
        streak=streak,
        today=date.today()
    )