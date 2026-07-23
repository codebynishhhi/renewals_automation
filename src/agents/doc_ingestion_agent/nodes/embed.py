import logging
import uuid
from src.common.database import AsyncSessionLocal
from src.agents.doc_ingestion_agent.state import DocumentIngestionAgentState
from fastembed import TextEmbedding
from src.api.models import DocumentChunks

logger = logging.getLogger()

# embed 20 chunks at once
BATCH_SIZE = 20

async def embed_and_store(state:DocumentIngestionAgentState) -> dict:
    """
    Node 3+4 combined - embed chunks and write to pgvector
    using fastembed for local embeddings instead of embedding model 
    """

    chunks = state["chunks"]
    artifact_id = uuid.UUID(str(state["artifact_id"]))

    # load local embedding model
    embed_model = TextEmbedding("BAAI/bge-small-en-v1.5")
    logger.info("Embed %d chunks | artifact=%s", len(chunks), artifact_id)

    embeddings_written = 0

    # Process in batches
    for batch_start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[batch_start : batch_start + BATCH_SIZE]
        text = [c["text"] for c in batch]

        # Generate the lists of text embeddings
        vectors = list(embed_model.embed(text))

        async with AsyncSessionLocal() as db:
            # 🌟 FIXED: Zipping batch against 'vectors' (plural) correctly now
            for chunk_data, vector in zip(batch, vectors):
                chunk = DocumentChunks(
                    artifact_id=artifact_id,
                    chunk_text=chunk_data["text"],
                    chunk_index=chunk_data["index"],
                    page_number=chunk_data["page"],
                    embedding=vector.tolist() # Converts NumPy array into standard Python float lists
                )
                db.add(chunk)
            await db.commit()
        
        embeddings_written += len(batch)
        logger.info("Written %d/%d chunks", embeddings_written, len(chunks))
    return {"embeddings_written":embeddings_written}


