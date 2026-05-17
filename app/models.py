from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    semesters = db.relationship(
        "Semester",
        backref="user",
        cascade="all, delete-orphan",
        lazy=True
    )


class Semester(db.Model):
    __tablename__ = "semesters"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    semester_number = db.Column(db.Integer, nullable=False)
    sgpa = db.Column(db.Float, default=0)

    subjects = db.relationship(
        "Subject",
        backref="semester",
        cascade="all, delete-orphan",
        lazy=True
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "semester_number",
            name="unique_user_semester"
        ),
    )


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    semester_id = db.Column(db.Integer, db.ForeignKey("semesters.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(5), nullable=False)
    grade_points = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            "semester_id",
            "name",
            name="unique_subject_per_semester"
        ),
    )