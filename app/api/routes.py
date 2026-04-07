from flask import Blueprint, jsonify, current_app, request
from ..models import User, Company, Branch, AuditLog, Permission, RolePermission

api = Blueprint("api", __name__)

def require_api_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False
    token = auth_header.replace("Bearer ", "", 1).strip()
    return token == current_app.config["API_TOKEN"]

@api.route("/health")
def health():
    return jsonify({"ok": True, "service": "whitelabel_login_v5_1"})

@api.route("/stats")
def stats():
    if not require_api_token():
        return jsonify({"error": "unauthorized"}), 401

    payload = {
        "users": User.query.count(),
        "active_users": User.query.filter_by(is_active_user=True).count(),
        "companies": Company.query.count(),
        "branches": Branch.query.count(),
        "audit_logs": AuditLog.query.count(),
        "roles": {
            "superadmin": User.query.filter_by(role="superadmin").count(),
            "admin": User.query.filter_by(role="admin").count(),
            "manager": User.query.filter_by(role="manager").count(),
            "user": User.query.filter_by(role="user").count(),
        }
    }
    return jsonify(payload)

@api.route("/users")
def users():
    if not require_api_token():
        return jsonify({"error": "unauthorized"}), 401

    data = [{
        "id": u.id,
        "full_name": u.full_name,
        "email": u.email,
        "role": u.role,
        "active": u.is_active_user,
        "company": u.company.name if u.company else None,
        "branch": u.branch.name if u.branch else None,
        "two_factor_email_enabled": u.two_factor_email_enabled,
        "two_factor_totp_enabled": u.two_factor_totp_enabled,
    } for u in User.query.order_by(User.id.asc()).all()]
    return jsonify(data)

@api.route("/permissions")
def permissions():
    if not require_api_token():
        return jsonify({"error": "unauthorized"}), 401

    result = {}
    for rp in RolePermission.query.order_by(RolePermission.role_name.asc()).all():
        result.setdefault(rp.role_name, []).append(rp.permission.name)

    perms = [p.name for p in Permission.query.order_by(Permission.name.asc()).all()]
    return jsonify({
        "permissions": perms,
        "matrix": result
    })
