import pytest
from app import create_app, db
from app.models import User, Company, Branch, Permission, RolePermission

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "API_TOKEN": "test-token",
    })

    with app.app_context():
        db.drop_all()
        db.create_all()

        company = Company(name="Empresa Test", code="EMPTEST")
        db.session.add(company)
        db.session.commit()

        branch = Branch(name="Sucursal Test", code="SUCTEST", company_id=company.id)
        db.session.add(branch)
        db.session.commit()

        perm = Permission(name="dashboard.view")
        db.session.add(perm)
        db.session.commit()

        rp = RolePermission(role_name="superadmin", permission_id=perm.id)
        db.session.add(rp)
        db.session.commit()

        user = User(
            full_name="Admin Test",
            email="admin@test.local",
            role="superadmin",
            company_id=company.id,
            branch_id=branch.id,
            is_active_user=True
        )
        user.set_password("secret123")
        db.session.add(user)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
