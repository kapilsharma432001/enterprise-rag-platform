from app.services.ingestion import embeddings_model
from app.utils import reciprocal_rank_fusion
import json

async def perform_hybrid_search(query_text: str, tenant_id: str, conn):

    """
    Runs keyword search and vector search and then fuses them
    """

    # Generate embedding for the query
    query_vector = embeddings_model.embed_query(query_text)
    vector_str = str(query_vector) # format for pgvector

    # vector search query
    # We fetch top 5 purely bassed on meaning

    vector_sql = """
        SELECT id, content, 
               1 - (embedding <=> $1) as similarity -- Cosine Similarity
        FROM documents 
        ORDER BY embedding <=> $1
        LIMIT 5;
    """

    # keyword search query
    # plainto_tsquery parses "Error 505" -> "'error' & '505'"
    keyword_sql = """
        SELECT id, content, 
               ts_rank(search_vector, plainto_tsquery('english', $1)) as rank
        FROM documents 
        WHERE search_vector @@ plainto_tsquery('english', $1)
        ORDER BY rank DESC
        LIMIT 5;
    """

    # 4. Execute both (The RLS Policy in 'conn' automatically filters by Tenant!)
    print(f"🔍 Searching for '{query_text}' in Tenant {tenant_id}...")

    vector_rows = await conn.fetch(vector_sql, vector_str)
    keyword_rows = await conn.fetch(keyword_sql, query_text)
    
    # convert to dictionaries
    vector_results = [dict(row) for row in vector_rows]
    keyword_results = [dict(row) for row in keyword_rows]

    print(f"Vector Results: len({vector_results})")
    print(f"Keyword Results: len({keyword_results})")

    # apply RRF fusion
    final_results = reciprocal_rank_fusion(keyword_results, vector_results)
    #print(f"Final Results: {json.dumps(final_results, indent=2)}")

    return final_results