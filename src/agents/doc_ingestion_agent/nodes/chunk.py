import logging 
from src.agents.doc_ingestion_agent.state import DocumentIngestionAgentState

logger = logging.getLogger(__name__)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

def chunk_documents(state: DocumentIngestionAgentState) -> dict:
    """
    Node 2 - Split page text into overlapping chunks
    Simple character based chunking
    """

    raw_pages = state["raw_pages"]
    chunks = []
    chunk_index = 0

    for page_data in raw_pages:
        text = page_data["text"]
        page_num = page_data["page"]
        start = 0

        while start < len(text):
            end = start + CHUNK_SIZE
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "text":chunk_text,
                    "page":page_num,
                    "index" :chunk_index
                })
            
            # overlap with previous chunk
            start += CHUNK_SIZE - CHUNK_OVERLAP

        logger.info("Created %d chunks from %d pages", len(chunks), len(raw_pages))
        return {"chunks":chunks}