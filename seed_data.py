from app import create_app, db
from app.models import Company, Branch, Permission, RolePermission, User

app = create_app()

DEFAULT_PERMISSIONS = [
    "dashboard.view",
    "users.view",
    "users.create",
    "users.update",
    "users.delete",
    "companies.view",
    "companies.create",
    "branches.view",
    "branches.create",
    "audit.view",
    "api.read",
]

ROLE_MATRIX = {
    "superadmin": DEFAULT_PERMISSIONS,
    "admin": [p for p in DEFAULT_PERMISSIONS if p != "users.delete"],
    "manager": ["dashboard.view", "users.view", "companies.view", "branches.view", "audit.view", "api.read"],
    "user": [],
}

with app.app_context():
    db.create_all()

    company = Company.query.filter_by(code="EMPDEMO").first()
    if not company:
        company = Company(name="Empresa Demo", code="EMPDEMO")
        db.session.add(company)
        db.session.commit()

    branch = Branch.query.filter_by(code="CASA-MATRIZ").first()
    if not branch:
        branch = Branch(name="Casa Matriz", code="CASA-MATRIZ", company_id=company.id)
        db.session.add(branch)
        db.session.commit()

    for perm_name in DEFAULT_PERMISSIONS:
        if not Permission.query.filter_by(name=perm_name).first():
            db.session.add(Permission(name=perm_name))
    db.session.commit()

    perms = {p.name: p for p in Permission.query.all()}
    for role, perm_list in ROLE_MATRIX.items():
        for perm_name in perm_list:
            exists = RolePermission.query.filter_by(role_name=role, permission_id=perms[perm_name].id).first()
            if not exists:
                db.session.add(RolePermission(role_name=role, permission_id=perms[perm_name].id))
    db.session.commit()

    user = User.query.filter_by(email="superadmin@local.test").first()
    if not user:
        user = User(
            full_name="Super Admin",
            email="superadmin@local.test",
            role="superadmin",
            company_id=company.id,
            branch_id=branch.id,
            is_active_user=True,
        )
        user.set_password("ChangeMe123!")
        db.session.add(user)
        db.session.commit()

    print("Datos iniciales cargados.")
