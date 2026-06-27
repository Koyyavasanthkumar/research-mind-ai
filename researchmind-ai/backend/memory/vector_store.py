from __future__ import annotations

import logging

import chromadb

from backend.models.schemas import ExtractedInformation
from backend.utils.config import settings

logger = logging.getLogger(__name__)


class ResearchMemory:
    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(path=settings.chroma_path)
        self.collection = self.client.get_or_create_collection("research_information")

    def store_information(self, research_id: str, information: list[ExtractedInformation]) -> None:
        documents: list[str] = []
        metadatas: list[dict[str, str]] = []
        ids: list[str] = []
        for info_idx, item in enumerate(information):
            claims = item.facts + item.statistics + item.important_statements + item.definitions + item.examples
            for claim_idx, claim in enumerate(claims):
                documents.append(claim)
                metadatas.append({"research_id": research_id, "source_url": item.source_url, "sub_topic": item.sub_topic})
                ids.append(f"{research_id}-{info_idx}-{claim_idx}")
        if not documents:
            return
        try:
            self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        except Exception:
            logger.exception("Failed to persist extracted information to ChromaDB")

    def query_related(self, query: str, limit: int = 5) -> list[str]:
        try:
            result = self.collection.query(query_texts=[query], n_results=limit)
            return result.get("documents", [[]])[0]
        except Exception:
            logger.exception("Failed to query ChromaDB")
            return []

    def store_text(self, user_id: int, content: str, metadata: dict) -> None:
        try:
            doc_id = f"user-{user_id}-{abs(hash(content))}"
            self.collection.upsert(
                ids=[doc_id],
                documents=[content],
                metadatas=[{"user_id": str(user_id), **{key: str(value) for key, value in metadata.items()}}],
            )
        except Exception:
            logger.exception("Failed to store user memory in ChromaDB")

    def search_user(self, user_id: int, query: str, limit: int = 5) -> list[str]:
        try:
            result = self.collection.query(query_texts=[query], n_results=limit, where={"user_id": str(user_id)})
            return result.get("documents", [[]])[0]
        except Exception:
            logger.exception("Failed to search user memory")
            return []

    def clear_user(self, user_id: int) -> None:
        try:
            matches = self.collection.get(where={"user_id": str(user_id)})
            ids = matches.get("ids", [])
            if ids:
                self.collection.delete(ids=ids)
        except Exception:
            logger.exception("Failed to clear user memory")


research_memory = ResearchMemory()
