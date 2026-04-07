from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_
from . import db
from .models import User, Company, Branch, AuditLog
from .security import permission_required, superadmin_required
from .utils import csv_response, write_audit

admin = Blueprint("admin", __name__, url_prefix="/admin")

@admin.route("/dashboard")
@login_required
@permission_required("dashboard.view")
def dashboard():
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active_user=True).count()
    total_companies = Company.query.count()
    total_branches = Branch.query.count()
    recent_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(12).all()

    role_counts = {
        "superadmin": User.query.filter_by(role="superadmin").count(),
        "admin": User.query.filter_by(role="admin").count(),
        "manager": User.query.filter_by(role="manager").count(),
        "user": User.query.filter_by(role="user").count(),
    }

    return render_template("admin/dashboard.html",
                           total_users=total_users,
                           active_users=active_users,
                           total_companies=total_companies,
                           total_branches=total_branches,
                           recent_logs=recent_logs,
                           role_counts=role_counts)

@admin.route("/users")
@login_required
@permission_required("users.view")
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    companies = Company.query.order_by(Company.name.asc()).all()
    branches = Branch.query.order_by(Branch.name.asc()).all()
    return render_template("admin/users.html", users=users, companies=companies, branches=branches)

@admin.route("/users/create", methods=["POST"])
@login_required
@permission_required("users.create")
def create_user():
    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    role = request.form.get("role", "user")
    company_id = request.form.get("company_id") or None
    branch_id = request.form.get("branch_id") or None

    if not full_name or not email or not password:
        flash("Completa los campos obligatorios.", "error")
        return redirect(url_for("admin.users"))

    if User.query.filter_by(email=email).first():
        flash("El correo ya existe.", "error")
        return redirect(url_for("admin.users"))

    user = User(full_name=full_name, email=email, role=role, company_id=company_id, branch_id=branch_id)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    write_audit(current_user.id, "admin_created_user", email)
    flash("Usuario creado.", "success")
    return redirect(url_for("admin.users"))

@admin.route("/users/<int:user_id>/update", methods=["POST"])
@login_required
@permission_required("users.update")
def update_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("admin.users"))

    user.full_name = request.form.get("full_name", user.full_name).strip()
    user.role = request.form.get("role", user.role)
    user.company_id = request.form.get("company_id") or None
    user.branch_id = request.form.get("branch_id") or None
    user.is_active_user = request.form.get("is_active_user") == "on"
    user.two_factor_email_enabled = request.form.get("two_factor_email_enabled") == "on"
    db.session.commit()
    write_audit(current_user.id, "admin_updated_user", user.email)
    flash("Usuario actualizado.", "success")
    return redirect(url_for("admin.users"))

@admin.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@permission_required("users.delete")
@superadmin_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("admin.users"))
    if user.id == current_user.id:
        flash("No puedes eliminar tu propio usuario.", "error")
        return redirect(url_for("admin.users"))

    email = user.email
    db.session.delete(user)
    db.session.commit()
    write_audit(current_user.id, "admin_deleted_user", email)
    flash("Usuario eliminado.", "success")
    return redirect(url_for("admin.users"))

@admin.route("/companies", methods=["GET", "POST"])
@login_required
@permission_required("companies.view")
def companies():
    if request.method == "POST":
        if not current_user.has_permission("companies.create"):
            return render_template("errors/403.html"), 403
        name = request.form.get("name", "").strip()
        code = request.form.get("code", "").strip().upper()
        if name and code and not Company.query.filter(or_(Company.name == name, Company.code == code)).first():
            db.session.add(Company(name=name, code=code))
            db.session.commit()
            write_audit(current_user.id, "admin_created_company", name)
            flash("Empresa creada.", "success")
        else:
            flash("Empresa inválida o duplicada.", "error")

    companies = Company.query.order_by(Company.name.asc()).all()
    return render_template("admin/companies.html", companies=companies)

@admin.route("/branches", methods=["GET", "POST"])
@login_required
@permission_required("branches.view")
def branches():
    if request.method == "POST":
        if not current_user.has_permission("branches.create"):
            return render_template("errors/403.html"), 403
        name = request.form.get("name", "").strip()
        code = request.form.get("code", "").strip().upper()
        company_id = request.form.get("company_id")
        if name and code and company_id and not Branch.query.filter_by(code=code).first():
            db.session.add(Branch(name=name, code=code, company_id=company_id))
            db.session.commit()
            write_audit(current_user.id, "admin_created_branch", name)
            flash("Sucursal creada.", "success")
        else:
            flash("Sucursal inválida o duplicada.", "error")

    branches = Branch.query.order_by(Branch.name.asc()).all()
    companies = Company.query.order_by(Company.name.asc()).all()
    return render_template("admin/branches.html", branches=branches, companies=companies)

@admin.route("/audit")
@login_required
@permission_required("audit.view")
def audit():
    action = request.args.get("action", "").strip()
    email = request.args.get("email", "").strip().lower()

    query = AuditLog.query.join(User, User.id == AuditLog.user_id, isouter=True)
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))

    logs = query.order_by(AuditLog.created_at.desc()).limit(500).all()
    return render_template("admin/audit.html", logs=logs, action=action, email=email)

@admin.route("/users/export")
@login_required
@permission_required("users.view")
def users_export():
    users = User.query.order_by(User.id.asc()).all()
    rows = [[u.id, u.full_name, u.email, u.role, u.company.name if u.company else "", u.branch.name if u.branch else "", "si" if u.is_active_user else "no"] for u in users]
    return csv_response("users.csv", ["id", "nombre", "correo", "rol", "empresa", "sucursal", "activo"], rows)
