from flask import Blueprint, render_template
from app.decorators import login_required, get_current_user
from app.utils import calculate_cgpa, get_semester_data, get_trend

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return render_template("home.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    user_id = get_current_user()

    cgpa, total_credits = calculate_cgpa(user_id)

    semester_data = get_semester_data(user_id)

    best_sem = max(semester_data, key=lambda x: x["sgpa"], default=None)
    worst_sem = min(semester_data, key=lambda x: x["sgpa"], default=None)

    trend = get_trend(semester_data)

    return render_template(
        "dashboard.html",
        cgpa=cgpa,
        total_credits=total_credits,
        best_sem=best_sem,
        worst_sem=worst_sem,
        trend=trend
    )