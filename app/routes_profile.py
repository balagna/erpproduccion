from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db
from .utils import write_audit, new_totp_secret, verify_totp, totp_uri, qr_base64

profile = Blueprint("profile", __name__, url_prefix="/profile")

@profile.route("/")
@login_required
def index():
    pending_secret = request.args.get("pending_secret")
    provisioning_uri = None
    qr_image = None
    if pending_secret:
        provisioning_uri = totp_uri(current_user.email, pending_secret, "PortalEmpresarialV5")
        qr_image = qr_base64(provisioning_uri)
    return render_template("profile/index.html", pending_secret=pending_secret, provisioning_uri=provisioning_uri, qr_image=qr_image)

@profile.route("/change-password", methods=["POST"])
@login_required
def change_password():
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not current_user.check_password(current_password):
        flash("La contraseña actual no es correcta.", "error")
        return redirect(url_for("profile.index"))
    if not new_password or new_password != confirm_password:
        flash("Las nuevas contraseñas no coinciden.", "error")
        return redirect(url_for("profile.index"))

    current_user.set_password(new_password)
    db.session.commit()
    write_audit(current_user.id, "profile_changed_password", current_user.email)
    flash("Contraseña actualizada.", "success")
    return redirect(url_for("profile.index"))

@profile.route("/enable-email-2fa", methods=["POST"])
@login_required
def enable_email_2fa():
    current_user.two_factor_email_enabled = True
    db.session.commit()
    write_audit(current_user.id, "profile_enabled_email_2fa", current_user.email)
    return redirect(url_for("profile.index"))

@profile.route("/disable-email-2fa", methods=["POST"])
@login_required
def disable_email_2fa():
    current_user.two_factor_email_enabled = False
    db.session.commit()
    write_audit(current_user.id, "profile_disabled_email_2fa", current_user.email)
    return redirect(url_for("profile.index"))

@profile.route("/start-totp", methods=["POST"])
@login_required
def start_totp():
    secret = new_totp_secret()
    return redirect(url_for("profile.index", pending_secret=secret))

@profile.route("/confirm-totp", methods=["POST"])
@login_required
def confirm_totp():
    secret = request.form.get("pending_secret", "")
    code = request.form.get("totp_code", "").strip()

    if not secret or not verify_totp(secret, code):
        flash("Código TOTP inválido.", "error")
        return redirect(url_for("profile.index", pending_secret=secret))

    current_user.totp_secret = secret
    current_user.two_factor_totp_enabled = True
    db.session.commit()
    write_audit(current_user.id, "profile_enabled_totp", current_user.email)
    flash("2FA por app activado.", "success")
    return redirect(url_for("profile.index"))

@profile.route("/disable-totp", methods=["POST"])
@login_required
def disable_totp():
    current_user.two_factor_totp_enabled = False
    current_user.totp_secret = None
    db.session.commit()
    write_audit(current_user.id, "profile_disabled_totp", current_user.email)
    return redirect(url_for("profile.index"))
