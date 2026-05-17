from flask import Blueprint, jsonify, session

from app.decorators import login_required, get_current_user
from app.utils import GRADE_POINTS, calculate_cgpa, get_semester_data, get_trend


api_bp = Blueprint("api", __name__)


@api_bp.route("/grades")
def grades():
    return jsonify(GRADE_POINTS)


@api_bp.route("/cgpa")
@login_required
def api_cgpa():
    user_id = get_current_user()
    cgpa, total_credits = calculate_cgpa(user_id)

    return jsonify({
        "cgpa": cgpa,
        "total_credits": total_credits
    })


@api_bp.route("/dashboard")
@login_required
def api_dashboard():
    user_id = get_current_user()

    cgpa, total_credits = calculate_cgpa(user_id)
    semester_data = get_semester_data(user_id)

    return jsonify({
        "cgpa": cgpa,
        "total_credits": total_credits,
        "best_sem": max(semester_data, key=lambda x: x["sgpa"], default=None),
        "worst_sem": min(semester_data, key=lambda x: x["sgpa"], default=None),
        "trend": get_trend(semester_data)
    })