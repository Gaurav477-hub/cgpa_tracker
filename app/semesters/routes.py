from flask import Blueprint, render_template, request, redirect, flash, abort

from app.extensions import db
from app.models import Semester, Subject
from app.decorators import login_required, get_current_user
from app.utils import (
    semester_to_dict,
    subject_to_dict,
    calculate_sgpa_from_subjects
)


semesters_bp = Blueprint("semesters", __name__)


@semesters_bp.route("/add_semester", methods=["GET", "POST"])
@login_required
def add_semester():
    if request.method == "POST":
        try:
            sem_no = int(request.form["semester_number"])

            if sem_no <= 0:
                flash("Invalid semester number", "error")
                return redirect(request.url)

        except ValueError:
            flash("Semester number must be a number", "error")
            return redirect(request.url)

        user_id = get_current_user()

        existing = Semester.query.filter_by(
            user_id=user_id,
            semester_number=sem_no
        ).first()

        if existing:
            flash("Semester already exists", "error")
            return redirect(request.url)

        semester = Semester(
            user_id=user_id,
            semester_number=sem_no,
            sgpa=0
        )

        db.session.add(semester)
        db.session.commit()

        flash("Semester added successfully", "success")
        return redirect("/semesters")

    return render_template("add_semester.html")


@semesters_bp.route("/semesters")
@login_required
def semesters():
    user_id = get_current_user()

    user_semesters = (
        Semester.query
        .filter_by(user_id=user_id)
        .order_by(Semester.semester_number)
        .all()
    )

    result = []

    for sem in user_semesters:
        sgpa = calculate_sgpa_from_subjects(sem.subjects)

        result.append({
            "id": sem.id,
            "semester_number": sem.semester_number,
            "sgpa": sgpa
        })

    return render_template("semesters.html", semesters=result)


@semesters_bp.route("/semester/<int:sem_id>")
@login_required
def semester_detail(sem_id):
    user_id = get_current_user()

    semester = Semester.query.filter_by(
        id=sem_id,
        user_id=user_id
    ).first()

    if not semester:
        abort(403)

    search = request.args.get("search", "").strip()
    grade_filter = request.args.get("grade", "").strip()
    sort = request.args.get("sort", "").strip()

    query = Subject.query.filter_by(semester_id=sem_id)

    if search:
        query = query.filter(Subject.name.ilike(f"%{search}%"))

    if grade_filter:
        query = query.filter(Subject.grade == grade_filter)

    if sort == "credits":
        query = query.order_by(Subject.credits.desc())
    elif sort == "grade":
        query = query.order_by(Subject.grade_points.desc())

    filtered_subjects = query.all()

    all_subjects = semester.subjects

    total_credits = sum(sub.credits for sub in all_subjects)
    total_points = sum(sub.credits * sub.grade_points for sub in all_subjects)

    sgpa = calculate_sgpa_from_subjects(all_subjects)

    subjects = [subject_to_dict(sub) for sub in filtered_subjects]

    no_results = bool((search or grade_filter) and len(subjects) == 0)

    return render_template(
        "semester_detail.html",
        semester=semester_to_dict(semester),
        subjects=subjects,
        sem_id=sem_id,
        total_credits=total_credits,
        total_points=total_points,
        sgpa=sgpa,
        no_results=no_results
    )


@semesters_bp.route("/edit_semester/<int:sem_id>", methods=["GET", "POST"])
@login_required
def edit_semester(sem_id):
    user_id = get_current_user()

    semester = Semester.query.filter_by(
        id=sem_id,
        user_id=user_id
    ).first()

    if not semester:
        abort(403)

    if request.method == "POST":
        try:
            new_number = int(request.form["semester_number"])

            if new_number <= 0:
                flash("Invalid semester number", "error")
                return redirect(request.url)

        except ValueError:
            flash("Semester number must be a number", "error")
            return redirect(request.url)

        duplicate = Semester.query.filter(
            Semester.user_id == user_id,
            Semester.semester_number == new_number,
            Semester.id != sem_id
        ).first()

        if duplicate:
            flash("Semester number already exists", "error")
            return redirect(request.url)

        semester.semester_number = new_number
        db.session.commit()

        flash("Semester updated successfully", "success")
        return redirect("/semesters")

    return render_template(
        "edit_semester.html",
        semester=semester_to_dict(semester)
    )


@semesters_bp.route("/delete_semester/<int:sem_id>", methods=["POST"])
@login_required
def delete_semester(sem_id):
    user_id = get_current_user()

    semester = Semester.query.filter_by(
        id=sem_id,
        user_id=user_id
    ).first()

    if not semester:
        abort(403)

    db.session.delete(semester)
    db.session.commit()

    flash("Semester deleted successfully", "success")
    return redirect("/semesters")