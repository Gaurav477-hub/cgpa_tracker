from flask import Blueprint, render_template, request, redirect, flash

from app.decorators import login_required, get_current_user
from app.models import Semester, Subject
from app.utils import (
    calculate_cgpa,
    get_semester_data,
    get_trend,
    get_grade_point
)


analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.route("/cgpa")
@login_required
def cgpa():
    user_id = get_current_user()

    cgpa_value, total_credits = calculate_cgpa(user_id)

    return render_template(
        "cgpa.html",
        cgpa=cgpa_value,
        total_credits=total_credits
    )


@analysis_bp.route("/analysis")
@login_required
def analysis():
    user_id = get_current_user()

    semester_data = get_semester_data(user_id)

    best_sem = max(semester_data, key=lambda x: x["sgpa"], default=None)
    worst_sem = min(semester_data, key=lambda x: x["sgpa"], default=None)

    trend = get_trend(semester_data)

    subjects = (
        Subject.query
        .join(Semester)
        .filter(Semester.user_id == user_id)
        .all()
    )

    top_subject = None
    weak_subject = None

    if subjects:
        # Best subject = highest grade point
        # If tie, higher credit subject is more meaningful
        top = max(
            subjects,
            key=lambda x: (get_grade_point(x.grade), x.credits)
        )

        # Weakest subject = lowest grade point
        # If tie, higher credit weak subject matters more
        weak = min(
            subjects,
            key=lambda x: (get_grade_point(x.grade), -x.credits)
        )

        top_subject = {
            "name": top.name,
            "grade": top.grade,
            "credits": top.credits,
            "grade_points": get_grade_point(top.grade)
        }

        weak_subject = {
            "name": weak.name,
            "grade": weak.grade,
            "credits": weak.credits,
            "grade_points": get_grade_point(weak.grade)
        }

    predicted_cgpa = None

    if semester_data:
        avg_sgpa = sum(s["sgpa"] for s in semester_data) / len(semester_data)

        if "Improving" in trend:
            predicted_cgpa = round(avg_sgpa + 0.3, 2)
        elif "Declining" in trend:
            predicted_cgpa = round(avg_sgpa - 0.3, 2)
        else:
            predicted_cgpa = round(avg_sgpa, 2)

    return render_template(
        "analysis.html",
        best_sem=best_sem,
        worst_sem=worst_sem,
        trend=trend,
        top_subject=top_subject,
        weak_subject=weak_subject,
        predicted_cgpa=predicted_cgpa
    )


@analysis_bp.route("/goal", methods=["GET", "POST"])
@login_required
def goal():
    required_sgpa = None
    message = None

    if request.method == "POST":
        try:
            target_cgpa = float(request.form["target_cgpa"])
            future_credits = int(request.form["future_credits"])

            if target_cgpa <= 0 or future_credits <= 0:
                flash("Invalid input values", "error")
                return redirect(request.url)

        except ValueError:
            flash("Enter valid numbers", "error")
            return redirect(request.url)

        user_id = get_current_user()

        cgpa, current_credits = calculate_cgpa(user_id)
        current_points = cgpa * current_credits

        required_sgpa = (
            target_cgpa * (current_credits + future_credits) - current_points
        ) / future_credits

        required_sgpa = round(required_sgpa, 2)

        if required_sgpa > 10:
            message = "Impossible 🚫 (Required SGPA > 10)"
        elif required_sgpa >= 9:
            message = "Very Hard ⚠️"
        elif required_sgpa >= 8:
            message = "Challenging"
        else:
            message = "Achievable ✅"

    return render_template(
        "goal.html",
        required_sgpa=required_sgpa,
        message=message
    )