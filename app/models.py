from datetime import datetime, UTC
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)

class Branch(db.Model):
    __tablename__ = "branches"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    company = db.relationship("Company", backref="branches")

class Permission(db.Model):
    __tablename__ = "permissions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)

class RolePermission(db.Model):
    __tablename__ = "role_permissions"
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(20), nullable=False, index=True)
    permission_id = db.Column(db.Integer, db.ForeignKey("permissions.id"), nullable=False, index=True)
    permission = db.relationship("Permission")

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user", index=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=True, index=True)
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"), nullable=True, index=True)
    is_active_user = db.Column(db.Boolean, default=True, nullable=False)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime(timezone=True), nullable=True)
    last_login_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    two_factor_email_enabled = db.Column(db.Boolean, default=False, nullable=False)
    two_factor_totp_enabled = db.Column(db.Boolean, default=False, nullable=False)
    totp_secret = db.Column(db.String(64), nullable=True)

    company = db.relationship("Company", backref="users")
    branch = db.relationship("Branch", backref="users")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return self.is_active_user

    def is_admin_like(self):
        return self.role in ("admin", "superadmin", "manager")

    def is_superadmin(self):
        return self.role == "superadmin"

    def has_permission(self, permission_name):
        if self.role == "superadmin":
            return True
        rows = RolePermission.query.filter_by(role_name=self.role).all()
        return any(r.permission.name == permission_name for r in rows)

class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    used = db.Column(db.Boolean, default=False, nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    user = db.relationship("User", backref="reset_tokens")

class EmailOTP(db.Model):
    __tablename__ = "email_otps"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    code = db.Column(db.String(12), nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    user = db.relationship("User", backref="email_otps")

class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    action = db.Column(db.String(120), nullable=False, index=True)
    detail = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    user = db.relationship("User", backref="audit_logs")
