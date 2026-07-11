from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user

from core.models import User, PhysicalProfile, Goal, MealSuggestion, NutritionPlan, ProgressCheckIn, WorkoutPlan, db
from core.services import get_current_profile, get_current_goal

configuracoes_bp = Blueprint("configuracoes", __name__)


@configuracoes_bp.route("/configuracoes")
@login_required
def configuracoes():
    profile = get_current_profile()
    goal = get_current_goal()
    return render_template(
        "configuracoes.html",
        profile=profile,
        goal=goal,
        active_page="configuracoes",
    )


@configuracoes_bp.route("/configuracoes/perfil", methods=["POST"])
@login_required
def configuracoes_perfil():
    name = request.form.get("nome", "").strip()
    email = request.form.get("email", "").strip().lower()

    if not name or not email:
        flash("Preencha nome e e-mail.")
        return redirect(url_for("configuracoes.configuracoes"))

    email_em_uso = User.query.filter(
        User.email == email, User.id != current_user.id
    ).first()

    if email_em_uso:
        flash("Esse e-mail ja esta em uso por outra conta.")
        return redirect(url_for("configuracoes.configuracoes"))

    current_user.name = name
    current_user.email = email
    db.session.commit()

    flash("Perfil atualizado com sucesso.")
    return redirect(url_for("configuracoes.configuracoes"))


@configuracoes_bp.route("/configuracoes/senha", methods=["POST"])
@login_required
def configuracoes_senha():
    senha_atual = request.form.get("senha_atual", "")
    nova_senha = request.form.get("nova_senha", "")
    confirmar_senha = request.form.get("confirmar_senha", "")

    if not current_user.check_password(senha_atual):
        flash("Senha atual incorreta.")
        return redirect(url_for("configuracoes.configuracoes"))

    if len(nova_senha) < 6:
        flash("A nova senha deve ter pelo menos 6 caracteres.")
        return redirect(url_for("configuracoes.configuracoes"))

    if nova_senha != confirmar_senha:
        flash("As senhas nao coincidem.")
        return redirect(url_for("configuracoes.configuracoes"))

    current_user.set_password(nova_senha)
    db.session.commit()

    flash("Senha alterada com sucesso.")
    return redirect(url_for("configuracoes.configuracoes"))


@configuracoes_bp.route("/configuracoes/fisico", methods=["POST"])
@login_required
def configuracoes_fisico():
    gender = request.form.get("genero")
    weight = request.form.get("peso")
    height = request.form.get("altura")
    age = request.form.get("idade")
    activity_level = request.form.get("atividade")
    objective = request.form.get("objetivo")
    target_weight = request.form.get("target_weight")

    db.session.add(
        PhysicalProfile(
            user_id=current_user.id,
            gender=gender,
            weight=float(weight),
            height=float(height),
            age=int(age),
            activity_level=activity_level or None,
        )
    )

    if objective:
        Goal.query.filter_by(
            user_id=current_user.id, is_active=True
        ).update({"is_active": False})

        db.session.add(
            Goal(
                user_id=current_user.id,
                objective=objective,
                target_weight=float(target_weight) if target_weight else None,
                is_active=True,
            )
        )

    db.session.commit()
    flash("Dados fisicos atualizados com sucesso.")
    return redirect(url_for("configuracoes.configuracoes"))


@configuracoes_bp.route("/configuracoes/excluir-conta", methods=["POST"])
@login_required
def configuracoes_excluir_conta():
    senha = request.form.get("senha", "")

    if not current_user.check_password(senha):
        flash("Senha incorreta. Sua conta nao foi excluida.")
        return redirect(url_for("configuracoes.configuracoes"))

    user_id = current_user.id

    MealSuggestion.query.filter_by(user_id=user_id).delete()
    NutritionPlan.query.filter_by(user_id=user_id).delete()
    ProgressCheckIn.query.filter_by(user_id=user_id).delete()
    WorkoutPlan.query.filter_by(user_id=user_id).delete()
    Goal.query.filter_by(user_id=user_id).delete()
    PhysicalProfile.query.filter_by(user_id=user_id).delete()

    user = db.session.get(User, user_id)
    db.session.delete(user)
    db.session.commit()

    logout_user()

    from flask import session
    session.clear()

    flash("Sua conta foi excluida com sucesso.")
    return redirect(url_for("home"))