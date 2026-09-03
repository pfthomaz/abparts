#!/usr/bin/env python3
"""
Rebuild the AutoBoss AI Assistant vector index from Postgres.

Use this after the FAISS index file is lost (e.g. the container was recreated
without a persistent volume) or after changing the embedding model. It reads
knowledge_documents + document_chunks and rebuilds data/vector_index - no source
PDFs required.

Usage (inside the container):
    docker compose exec ai_assistant python reindex_knowledge.py
    docker compose exec ai_assistant python reindex_knowledge.py --re-embed

--re-embed forces every chunk to be re-embedded from its text (required when
OPENAI_EMBEDDING_MODEL / EMBEDDING_DIMENSION changed). Without it, embeddings
already stored for the current model are reused and only missing ones are generated.

You can also just call the HTTP endpoint:
    curl -X POST 'http://localhost:8001/knowledge/reindex?re_embed=false'
"""

import argparse
import asyncio
import json

from app.llm_client import LLMClient
from app.services.vector_database import VectorDatabase
from app.services.knowledge_base import KnowledgeBaseService


async def main(re_embed: bool) -> None:
    llm_client = LLMClient()
    await llm_client.initialize()

    service = KnowledgeBaseService(llm_client, VectorDatabase())

    print(f"Reindexing knowledge base (re_embed={re_embed}) ...")
    summary = await service.reindex_from_database(re_embed=re_embed)
    print(json.dumps(summary, indent=2, default=str))

    await llm_client.cleanup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rebuild the AI Assistant vector index from Postgres")
    parser.add_argument("--re-embed", action="store_true",
                        help="Re-embed every chunk from text (use after changing the embedding model)")
    args = parser.parse_args()
    asyncio.run(main(args.re_embed))
