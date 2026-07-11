from flask import Blueprint, render_template

institucional_bp = Blueprint("institucional", __name__)


@institucional_bp.route("/sobre")
def about():
    return render_template("about.html")


@institucional_bp.route("/privacidade")
def privacy():
    return render_template("privacy.html")


@institucional_bp.route("/suporte")
def support():
    return render_template("support.html")


@institucional_bp.route("/funcionalidades")
def features():
    return render_template("features.html")