from flask import Flask
from app.extensions import db


def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )

    app.config.from_object("app.config.Config")

    db.init_app(app)

    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.semesters.routes import semesters_bp
    from app.subjects.routes import subjects_bp
    from app.analysis.routes import analysis_bp
    from app.api_routes.routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(semesters_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    return app