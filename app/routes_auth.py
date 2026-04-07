from datetime import timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from flask_login import login_user, logout_user, current_user
from . import db
from .models import User, PasswordResetToken
from .utils import utcnow, write_audit, create_password_reset_token, create_email_otp, verify_email_otp, verify_totp
from .services.mail_service import send_email

auth = Blueprint("auth", __name__)

def _is_locked(user):
    return user.locked_until is not None and user.locked_until > utcnow()

@auth.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("auth.login"))

@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Credenciales inválidas.", "error")
            return render_template("auth/login.html")

        if _is_locked(user):
            flash("Tu cuenta está bloqueada temporalmente.", "error")
            write_audit(user.id, "login_blocked_locked", email)
            return render_template("auth/login.html")

        if not user.check_password(password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= current_app.config["SECURITY_MAX_LOGIN_ATTEMPTS"]:
                user.locked_until = utcnow() + timedelta(minutes=current_app.config["SECURITY_LOCK_MINUTES"])
            db.session.commit()
            flash("Credenciales inválidas.", "error")
            write_audit(user.id, "login_failed", email)
            return render_template("auth/login.html")

        if not user.is_active_user:
            flash("Usuario desactivado.", "error")
            return render_template("auth/login.html")

        if user.two_factor_email_enabled or user.two_factor_totp_enabled:
            session["pre_2fa_user_id"] = user.id
            if user.two_factor_email_enabled:
                code = create_email_otp(user.id)
                send_email("Código de verificación", user.email, f"Tu código es: {code}")
            write_audit(user.id, "login_pending_2fa", "Contraseña correcta")
            return redirect(url_for("auth.two_factor"))

        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = utcnow()
        db.session.commit()
        login_user(user)
        write_audit(user.id, "login_success", "Inicio exitoso")
        return redirect(url_for("admin.dashboard"))

    return render_template("auth/login.html")

@auth.route("/two-factor", methods=["GET", "POST"])
def two_factor():
    user_id = session.get("pre_2fa_user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    user = db.session.get(User, user_id)
    if not user:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        email_code = request.form.get("email_code", "").strip()
        totp_code = request.form.get("totp_code", "").strip()

        if user.two_factor_email_enabled and not verify_email_otp(user.id, email_code):
            flash("Código de correo inválido.", "error")
            return render_template("auth/two_factor.html", need_email=user.two_factor_email_enabled, need_totp=user.two_factor_totp_enabled)

        if user.two_factor_totp_enabled and not verify_totp(user.totp_secret, totp_code):
            flash("Código de app inválido.", "error")
            return render_template("auth/two_factor.html", need_email=user.two_factor_email_enabled, need_totp=user.two_factor_totp_enabled)

        login_user(user)
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = utcnow()
        db.session.commit()
        session.pop("pre_2fa_user_id", None)
        write_audit(user.id, "login_success_2fa", "Inicio con 2FA")
        return redirect(url_for("admin.dashboard"))

    return render_template("auth/two_factor.html", need_email=user.two_factor_email_enabled, need_totp=user.two_factor_totp_enabled)

@auth.route("/register", methods=["GET", "POST"])
def register():
    from .models import Company, Branch
    companies = Company.query.order_by(Company.name.asc()).all()
    branches = Branch.query.order_by(Branch.name.asc()).all()

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        company_id = request.form.get("company_id") or None
        branch_id = request.form.get("branch_id") or None

        if not full_name or not email or not password:
            flash("Completa los campos obligatorios.", "error")
            return render_template("auth/register.html", companies=companies, branches=branches)

        if User.query.filter_by(email=email).first():
            flash("El correo ya existe.", "error")
            return render_template("auth/register.html", companies=companies, branches=branches)

        user = User(full_name=full_name, email=email, role="user", company_id=company_id, branch_id=branch_id)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        write_audit(user.id, "user_register", email)
        flash("Cuenta creada.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", companies=companies, branches=branches)

@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            token = create_password_reset_token(user.id)
            reset_url = url_for("auth.reset_password", token=token, _external=True)
            send_email("Recuperación de contraseña", user.email, f"Usa este enlace: {reset_url}")
            write_audit(user.id, "password_reset_requested", email)
        flash("Si el correo existe, se envió un enlace.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/forgot_password.html")

@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    row = PasswordResetToken.query.filter_by(token=token, used=False).first()
    if not row or row.expires_at < utcnow():
        flash("Token inválido o expirado.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if not password or password != confirm:
            flash("Las contraseñas no coinciden.", "error")
            return render_template("auth/reset_password.html")

        user = row.user
        user.set_password(password)
        row.used = True
        user.failed_login_attempts = 0
        user.locked_until = None
        db.session.commit()
        write_audit(user.id, "password_reset_completed", user.email)
        flash("Contraseña actualizada.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html")

@auth.route("/logout")
def logout():
    if current_user.is_authenticated:
        write_audit(current_user.id, "logout", "Sesión cerrada")
        logout_user()
    session.pop("pre_2fa_user_id", None)
    return redirect(url_for("auth.login"))
