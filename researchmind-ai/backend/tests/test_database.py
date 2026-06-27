from backend.database.session import SessionLocal, init_db
from backend.models.database import User
from backend.services.auth_service import AuthService


def test_database_create_user() -> None:
    init_db()
    db = SessionLocal()
    try:
        service = AuthService(db)
        user = service.users.get_by_email("db@example.com") or service.users.create(
            "db@example.com",
            "Database User",
            service.hash_password("StrongPass123"),
        )
        assert isinstance(user, User)
        assert user.email == "db@example.com"
    finally:
        db.close()
