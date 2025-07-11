from superset import create_app
from flask_appbuilder.security.sqla.models import User
from flask_appbuilder.security.manager import AUTH_DB
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    from superset.extensions import db, security_manager

    username = "admin1"
    first_name = "S"
    last_name = "N"
    email = "srikanthnarayanan0@gmail.com"
    password = "Srik@2025"  # ⚠️ Change this

    user = db.session.query(User).filter_by(username=username).first()
    if not user:
        user = security_manager.add_user(
            username,
            first_name,
            last_name,
            email,
            role=security_manager.find_role("Admin"),
            password=password,
        )
        print("✅ Admin user created.")
    else:
        print("ℹ️ User already exists.")
