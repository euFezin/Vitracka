from flask import Blueprint, flash, render_template, request, redirect, url_for, session
from flask_login import current_user, login_user, logout_user
from core.extensions import limiter
from datetime import datetime

from core.models import User, db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/cadastro", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        name = request.form["nome"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["senha"]
        aceite_termos = request.form.get("aceite_termos")

        if not aceite_termos:
            flash("Voce precisa aceitar os Termos de Uso para se cadastrar.")
            return redirect(url_for("auth.cadastro"))

        if User.query.filter_by(email=email).first():
            flash("Esse e-mail ja esta cadastrado. Entre na sua conta.")
            return redirect(url_for("auth.login"))

        user = User(name=name, email=email)
        user.set_password(password)
        user.terms_accepted_at = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("onboarding.objetivo"))

    return render_template("cadastro.html")


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["senha"]
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("E-mail ou senha invalidos.")
            return redirect(url_for("auth.login"))

        login_user(user)
        next_page = request.args.get("next")
        if next_page and next_page.startswith("/"):
            return redirect(next_page)
        return redirect(url_for("dashboard.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("home"))