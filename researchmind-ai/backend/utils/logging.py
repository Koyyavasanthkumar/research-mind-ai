import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from backend.config.settings import settings


def configure_logging() -> None:
    Path(settings.logs_dir).mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        Path(settings.logs_dir) / "researchmind.log",
        maxBytes=5_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[logging.StreamHandler(), file_handler],
    )
