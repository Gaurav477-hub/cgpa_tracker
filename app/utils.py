from app.models import Semester, Subject


GRADE_POINTS = {
    "O": 10,
    "A+": 9,
    "A": 8,
    "B+": 7,
    "B": 6,
    "C": 5,
    "P": 4,
    "F": 0
}


def is_valid_grade(grade):
    return grade in GRADE_POINTS


def get_grade_point(grade):
    return GRADE_POINTS.get(grade, 0)


def subject_to_dict(subject):
    gp = get_grade_point(subject.grade)

    return {
        "id": subject.id,
        "semester_id": subject.semester_id,
        "name": subject.name,
        "credits": subject.credits,
        "grade": subject.grade,
        "grade_points": gp
    }


def semester_to_dict(semester):
    return {
        "id": semester.id,
        "semester_number": semester.semester_number,
        "sgpa": semester.sgpa
    }


def calculate_sgpa_from_subjects(subjects):
    total_points = 0
    total_credits = 0

    for sub in subjects:
        gp = get_grade_point(sub.grade)
        total_points += sub.credits * gp
        total_credits += sub.credits

    if total_credits == 0:
        return 0

    return round(total_points / total_credits, 2)


def calculate_cgpa(user_id):
    subjects = (
        Subject.query
        .join(Semester)
        .filter(Semester.user_id == user_id)
        .all()
    )

    total_points = 0
    total_credits = 0

    for sub in subjects:
        gp = get_grade_point(sub.grade)
        total_points += sub.credits * gp
        total_credits += sub.credits

    if total_credits == 0:
        return 0, 0

    return round(total_points / total_credits, 2), total_credits


def update_semester_sgpa(semester):
    semester.sgpa = calculate_sgpa_from_subjects(semester.subjects)


def get_semester_data(user_id):
    semesters = (
        Semester.query
        .filter_by(user_id=user_id)
        .order_by(Semester.semester_number)
        .all()
    )

    data = []

    for sem in semesters:
        sgpa = calculate_sgpa_from_subjects(sem.subjects)

        if sgpa > 0:
            data.append({
                "sem_no": sem.semester_number,
                "sgpa": sgpa
            })

    return data


def get_trend(semester_data):
    if len(semester_data) >= 3:
        last_three = semester_data[-3:]

        if last_three[2]["sgpa"] > last_three[1]["sgpa"] > last_three[0]["sgpa"]:
            return "Strongly Improving 📈"

        if last_three[2]["sgpa"] < last_three[1]["sgpa"] < last_three[0]["sgpa"]:
            return "Strongly Declining 📉"

        return "Fluctuating"

    if len(semester_data) >= 2:
        if semester_data[-1]["sgpa"] > semester_data[-2]["sgpa"]:
            return "Improving 📈"

        if semester_data[-1]["sgpa"] < semester_data[-2]["sgpa"]:
            return "Declining 📉"

        return "Stable"

    return "Not enough data"