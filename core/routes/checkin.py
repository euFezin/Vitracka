from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from core.models import ProgressCheckIn, db

checkin_bp = Blueprint("checkin", __name__)


@checkin_bp.route("/check-in", methods=["GET", "POST"])
@login_required
def check_in():
    if request.method == "POST":
        waist = request.form.get("cintura", "").strip()
        notes = request.form.get("observacoes", "").strip()

        db.session.add(
            ProgressCheckIn(
                user_id=current_user.id,
                weight=float(request.form["peso"]),
                waist=float(waist) if waist else None,
                notes=notes or None,
            )
        )
        db.session.commit()
        return redirect(url_for("dashboard.dashboard"))

    return render_template("check_in.html")