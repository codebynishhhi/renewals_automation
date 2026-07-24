import logging
from src.agents.rule_extraction_agent.state import RuleExtractionAgentState
import uuid
from sqlalchemy import select, text
from src.common.database import AsyncSessionLocal
from src.api.models import DocumentChunks
from fastembed import TextEmbedding

logger = logging.getLogger(__name__)

TOP_K = 3

async def retrieve_context(state: RuleExtractionAgentState) -> dict:
    """ For each query embed the query & find the most similar chunks. Uses pgvector cosine similarity serach. """
    search_queries = state["retrieval_queries"]
    artifact_id = uuid.UUID(str(state["artifact_id"]))
    embed_model = TextEmbedding("BAAI/bge-small-en-v1.5")

    # set to keep a track of duplicate chunks
    seen_chunks_ids = set()
    retrieved_chunks = []

    # This function is doing a Vector Similarity Search. Its job is to take a user's search question, 
    # convert it into numbers (embeddings), and find the exact pages/text fragments inside your database that match the meaning of that question.
    async with AsyncSessionLocal() as db:
        for query in search_queries:
            #  get each query from search_queries [] & embed them
            query_vector = list(embed_model.embed([query]))[0].tolist()
            vector_str = "[" + ",".join(str(x) for x in query_vector) + "]"

            # <=>: This is the pgvector Cosine Distance operator.It calculates the space angle between your question's numbers and your stored document chunk numbers.
            result = await db.execute(
                text(
                    """
                    Select id, chunk_text, page_number, chunk_index, embedding <=> CAST(:vec AS vector) AS distance 
                    FROM document_chunks
                    WHERE artifact_id = :artifact_id
                    ORDER BY embedding <=> CAST(:vec AS vector)
                    LIMIT : top_k
                    """
                ),
                {
                    "vec" : vector_str, "artifact_id": str(artifact_id), "top_k":TOP_K
                }
            )
            rows = result.fetchall()

            for row in rows:
                if row.id not in seen_chunks_ids:
                    seen_chunks_ids.add(row.id)
                    retrieved_chunks.append(
                       {
                           "chunks_id": str(row.id),
                           "text" : row.chunk_text,
                           "page" :row.page_number,
                           "similarity" : round(1- row.distance, 4)
                       }

                    )


# Let us dry-run this exact code line-by-line using your input list: search_queries = ["abcugsw", "hxvhxvw"].
# Here is exactly how the data changes shapes at each step.
# Step 1: The Loop StartsThe for query in search_queries: loop picks the very first string:query = "abcugsw"

# Step 2: embed_model.embed([query])Notice you wrapped query inside brackets: [query]. This makes it a list of one string: ["abcugsw"].
# The model processes this batch and returns a generator containing NumPy arrays.Data shape: <generator object at 0x7f...>

# Step 3: list(...)Wrapping the generator in list() forces it to compute and turns it into a standard Python list containing a NumPy array.Data shape: [ array([0.12, -0.34, 0.56]) ]Visual Anchor: Notice the outer [ and ] brackets. Inside sits one single NumPy array object.
# 
# Step 4: [0]This index operation extracts the very first element out of that outer list. It strips away the outermost layer of brackets.Data shape: array([0.12, -0.34, 0.56])Visual Anchor: The outer list is gone. You are now holding just the raw NumPy array.
# 
# Step 5: .tolist()This NumPy method converts the math array into a native Python list of decimal numbers (floats).Data shape: [0.12, -0.34, 0.56]query_vector now equals this clean Python list.
# 
# Step 6: vector_str = ...Your code loops through every float in query_vector, joins them with commas, and wraps them in a string.Data shape: "[0.12,-0.34,0.56]" (This is a literal piece of text).
# 
# Step 7: The Database QueryYour SQL query takes that string "[0.12,-0.34,0.56]" and hands it to Postgres:sqlCAST('[0.12,-0.34,0.56]' AS vector)
# Use code with caution.Pgvector reads this text string and converts it into a database-native vector to calculate your cosine distances.