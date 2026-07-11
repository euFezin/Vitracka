from flask import Blueprint, redirect, url_for
from flask_login import login_required, current_user

from core.models import WorkoutPlan, db
from core.workout import gerar_treino
from core.services import get_current_profile, get_current_goal

treino_bp = Blueprint("treino", __name__)


@treino_bp.route("/treino")
@login_required
def treino():
    profile = get_current_profile()
    goal = get_current_goal()

    if not profile or not goal:
        return redirect(url_for("dashboard.dashboard"))

    treino_gerado = gerar_treino(profile, goal)

    workout = WorkoutPlan.query.filter_by(
        user_id=current_user.id
    ).first()

    if workout:
        workout.content = treino_gerado
    else:
        workout = WorkoutPlan(
            user_id=current_user.id,
            content=treino_gerado
        )
        db.session.add(workout)

    db.session.commit()
    return redirect(url_for("dashboard.dashboard"))