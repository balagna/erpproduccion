import io
import csv
import secrets
from datetime import datetime, timedelta, UTC
from flask import current_app, request, Response
import pyotp
import qrcode
import base64
from . import db
from .models import AuditLog, PasswordResetToken, EmailOTP

def utcnow():
    return datetime.now(UTC)

def client_ip():
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr

def write_audit(user_id, action, detail=None):
    db.session.add(AuditLog(user_id=user_id, action=action, detail=detail, ip_address=client_ip()))
    db.session.commit()

def create_password_reset_token(user_id):
    token = secrets.token_urlsafe(32)
    expires = utcnow() + timedelta(minutes=current_app.config["RESET_TOKEN_EXPIRES_MINUTES"])
    db.session.add(PasswordResetToken(user_id=user_id, token=token, expires_at=expires, used=False))
    db.session.commit()
    return token

def create_email_otp(user_id):
    code = f"{secrets.randbelow(1000000):06d}"
    expires = utcnow() + timedelta(minutes=current_app.config["EMAIL_OTP_EXPIRES_MINUTES"])
    db.session.add(EmailOTP(user_id=user_id, code=code, expires_at=expires, used=False))
    db.session.commit()
    return code

def verify_email_otp(user_id, code):
    row = EmailOTP.query.filter_by(user_id=user_id, code=code, used=False).order_by(EmailOTP.created_at.desc()).first()
    if not row or row.expires_at < utcnow():
        return False
    row.used = True
    db.session.commit()
    return True

def new_totp_secret():
    return pyotp.random_base32()

def verify_totp(secret, code):
    return pyotp.TOTP(secret).verify(code, valid_window=1)

def totp_uri(email, secret, issuer):
    return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)

def qr_base64(data):
    img = qrcode.make(data)
    buff = io.BytesIO()
    img.save(buff, format="PNG")
    return base64.b64encode(buff.getvalue()).decode("utf-8")

def csv_response(filename, headers, rows):
    sio = io.StringIO()
    writer = csv.writer(sio)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return Response(sio.getvalue(), mimetype="text/csv", headers={"Content-Disposition": f"attachment; filename={filename}"})
