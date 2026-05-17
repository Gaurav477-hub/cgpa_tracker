from flask import Blueprint, render_template, request, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import User
from app.decorators import login_required


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        confirm_password = request.form.get("confirm_password")

        if not username:
            flash("Username is required", "error")
            return redirect(request.url)

        if len(password) < 6:
            flash("Password must be at least 6 characters", "error")
            return redirect(request.url)

        if confirm_password is not None and password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(request.url)

        user = User(
            username=username,
            password=generate_password_hash(password)
        )

        try:
            db.session.add(user)
            db.session.commit()
            flash("Registration successful. Please login.", "success")
            return redirect("/login")

        except IntegrityError:
            db.session.rollback()
            flash("Username already exists", "error")
            return redirect(request.url)

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            flash("Login successful", "success")
            return redirect("/dashboard")

        flash("Invalid username or password", "error")
        return redirect("/login")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect("/login")