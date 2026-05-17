from flask import Blueprint, render_template, request, redirect, flash, abort

from app.extensions import db
from app.models import Semester, Subject
from app.decorators import login_required, get_current_user
from app.utils import (
    GRADE_POINTS,
    is_valid_grade,
    get_grade_point,
    subject_to_dict,
    update_semester_sgpa
)


subjects_bp = Blueprint("subjects", __name__)


@subjects_bp.route("/add_subject/<int:sem_id>", methods=["GET", "POST"])
@login_required
def add_subject(sem_id):
    user_id = get_current_user()

    semester = Semester.query.filter_by(
        id=sem_id,
        user_id=user_id
    ).first()

    if not semester:
        abort(403)

    if request.method == "POST":
        name = request.form["name"].strip()
        grade = request.form["grade"].strip().upper()

        if not name:
            flash("Invalid subject name", "error")
            return redirect(request.url)

        try:
            credits = int(request.form["credits"])

            if credits <= 0:
                flash("Credits must be positive", "error")
                return redirect(request.url)

        except ValueError:
            flash("Credits must be a number", "error")
            return redirect(request.url)

        if not is_valid_grade(grade):
            flash("Invalid grade", "error")
            return redirect(request.url)

        existing = Subject.query.filter_by(
            semester_id=sem_id,
            name=name
        ).first()

        if existing:
            flash("Subject already exists in this semester", "error")
            return redirect(request.url)

        subject = Subject(
            semester_id=sem_id,
            name=name,
            credits=credits,
            grade=grade,
            grade_points=get_grade_point(grade)
        )

        db.session.add(subject)

        update_semester_sgpa(semester)

        db.session.commit()

        flash("Subject added successfully", "success")
        return redirect(f"/semester/{sem_id}")

    return render_template("add_subject.html", sem_id=sem_id)


@subjects_bp.route("/edit_subject/<int:sub_id>/<int:sem_id>", methods=["GET", "POST"])
@login_required
def edit_subject(sub_id, sem_id):
    user_id = get_current_user()

    subject = (
        Subject.query
        .join(Semester)
        .filter(
            Subject.id == sub_id,
            Subject.semester_id == sem_id,
            Semester.user_id == user_id
        )
        .first()
    )

    if not subject:
        abort(403)

    semester = Semester.query.filter_by(
        id=sem_id,
        user_id=user_id
    ).first()

    if request.method == "POST":
        name = request.form["name"].strip()
        grade = request.form["grade"].strip().upper()

        if not name:
            flash("Invalid subject name", "error")
            return redirect(request.url)

        try:
            credits = int(request.form["credits"])

            if credits <= 0:
                flash("Credits must be positive", "error")
                return redirect(request.url)

        except ValueError:
            flash("Credits must be a number", "error")
            return redirect(request.url)

        if not is_valid_grade(grade):
            flash("Invalid grade", "error")
            return redirect(request.url)

        duplicate = Subject.query.filter(
            Subject.semester_id == sem_id,
            Subject.name == name,
            Subject.id != sub_id
        ).first()

        if duplicate:
            flash("Subject already exists", "error")
            return redirect(request.url)

        subject.name = name
        subject.credits = credits
        subject.grade = grade
        subject.grade_points = get_grade_point(grade)

        update_semester_sgpa(semester)

        db.session.commit()

        flash("Subject updated successfully", "success")
        return redirect(f"/semester/{sem_id}")

    return render_template(
        "edit_subject.html",
        subject=subject_to_dict(subject),
        sem_id=sem_id
    )


@subjects_bp.route("/delete_subject/<int:sub_id>/<int:sem_id>", methods=["POST"])
@login_required
def delete_subject(sub_id, sem_id):
    user_id = get_current_user()

    subject = (
        Subject.query
        .join(Semester)
        .filter(
            Subject.id == sub_id,
            Subject.semester_id == sem_id,
            Semester.user_id == user_id
        )
        .first()
    )

    if not subject:
        abort(403)

    semester = Semester.query.filter_by(
        id=sem_id,
        user_id=user_id
    ).first()

    db.session.delete(subject)

    update_semester_sgpa(semester)

    db.session.commit()

    flash("Subject deleted successfully", "success")
    return redirect(f"/semester/{sem_id}")


@subjects_bp.route("/simulate/<int:sem_id>", methods=["GET", "POST"])
@login_required
def simulate(sem_id):
    user_id = get_current_user()

    semester = Semester.query.filter_by(
        id=sem_id,
        user_id=user_id
    ).first()

    if not semester:
        abort(403)

    subjects = semester.subjects
    simulated_sgpa = None

    if request.method == "POST":
        total_points = 0
        total_credits = 0

        for sub in subjects:
            selected_grade = request.form.get(str(sub.id), sub.grade)

            if not is_valid_grade(selected_grade):
                selected_grade = sub.grade

            gp = get_grade_point(selected_grade)

            total_points += sub.credits * gp
            total_credits += sub.credits

        if total_credits > 0:
            simulated_sgpa = round(total_points / total_credits, 2)

    return render_template(
        "simulate.html",
        subjects=[subject_to_dict(sub) for sub in subjects],
        result=simulated_sgpa,
        sem_id=sem_id,
        grades=list(GRADE_POINTS.keys())
    )