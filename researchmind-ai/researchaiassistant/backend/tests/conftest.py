import os
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_researchmind.db")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("CHROMA_PATH", "./test_chroma")
os.environ.setdefault("REPORTS_DIR", "./test_reports")
os.environ.setdefault("LOGS_DIR", "./test_logs")

from fastapi.testclient import TestClient  # noqa: E402

from backend.main import app  # noqa: E402


def cleanup() -> None:
    for file_name in ("test_researchmind.db",):
        path = Path(file_name)
        if path.exists():
            path.unlink()


client = TestClient(app)

