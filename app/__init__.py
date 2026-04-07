import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Debes iniciar sesión para continuar."

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///local.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["APP_NAME"] = os.getenv("APP_NAME", "Portal Empresarial V5")
    app.config["APP_LOGO_TEXT"] = os.getenv("APP_LOGO_TEXT", app.config["APP_NAME"])
    app.config["PRIMARY_COLOR"] = os.getenv("PRIMARY_COLOR", "#111827")
    app.config["SECONDARY_COLOR"] = os.getenv("SECONDARY_COLOR", "#0f172a")
    app.config["DEBUG"] = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.config["SECURITY_MAX_LOGIN_ATTEMPTS"] = int(os.getenv("SECURITY_MAX_LOGIN_ATTEMPTS", "5"))
    app.config["SECURITY_LOCK_MINUTES"] = int(os.getenv("SECURITY_LOCK_MINUTES", "15"))
    app.config["RESET_TOKEN_EXPIRES_MINUTES"] = int(os.getenv("RESET_TOKEN_EXPIRES_MINUTES", "30"))
    app.config["EMAIL_OTP_EXPIRES_MINUTES"] = int(os.getenv("EMAIL_OTP_EXPIRES_MINUTES", "10"))
    app.config["MAIL_ENABLED"] = os.getenv("MAIL_ENABLED", "False").lower() == "true"
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", "587"))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    app.config["MAIL_USE_SSL"] = os.getenv("MAIL_USE_SSL", "False").lower() == "true"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "")
    app.config["MAIL_FROM"] = os.getenv("MAIL_FROM", "no-reply@example.com")
    app.config["API_TOKEN"] = os.getenv("API_TOKEN", "change-this-api-token")

    db.init_app(app)
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from .routes_auth import auth
    from .routes_admin import admin
    from .routes_profile import profile
    from .api.routes import api

    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(profile)
    app.register_blueprint(api, url_prefix="/api")

    @app.context_processor
    def inject_globals():
        return {
            "app_name": app.config["APP_NAME"],
            "app_logo_text": app.config["APP_LOGO_TEXT"],
            "primary_color": app.config["PRIMARY_COLOR"],
            "secondary_color": app.config["SECONDARY_COLOR"],
        }

    @app.errorhandler(403)
    def forbidden(_):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(_):
        return render_template("errors/404.html"), 404

    return app
