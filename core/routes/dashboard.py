from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import date

dashboard_bp = Blueprint("dashboard", __name__)

from core.services import calcular_streak, montar_dados_dashboard

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    dados = montar_dados_dashboard(current_user.id)

    return render_template(
        "dashboard.html",
        **dados,
        today=date.today()
    )