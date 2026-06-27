import logging

from backend.database.session import SessionLocal
from backend.repositories.research_repository import ResearchRepository

logger = logging.getLogger(__name__)


def recover_interrupted_research() -> int:
    db = SessionLocal()
    try:
        count = ResearchRepository(db).recover_interrupted_projects()
        if count:
            logger.warning("Recovered %s interrupted research projects", count)
        return count
    finally:
        db.close()
