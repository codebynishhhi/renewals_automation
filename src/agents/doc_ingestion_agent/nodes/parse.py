import logging
from src.common.minio_client import download_file

logger = logging.getLogger(__name__)

def parse_documents(state:dict) -> dict:
    """
    Node 1 - download the pdf from minio, extract the text page by page
    use pymupdf to extract text page by page
    """
    # pymupdf
    import fitz

    # get the storage key from state
    storage_key = state["storage_key"]
    logger.info("Parsing documents | key= %s", storage_key)

    pdf_bytes = download_file(storage_key)
    doc = fitz.open(stream = pdf_bytes, filetype = "pdf")

    raw_pages =[]
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text().strip()
        if text:
            raw_pages.append({"page":page_num+1, "text":text})
        
    doc.close()
    logger.info("Parsed %d pages| key = %s", len(raw_pages), storage_key)

    return {"raw_pages":raw_pages}


