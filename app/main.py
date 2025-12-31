from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Depends, Header
from app.db import db, get_db_connection
from app.services.ingestion import process_file
from pydantic import BaseModel
from app.services.search import perform_hybrid_search

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup code
    await db.connect()
    yield
    # shutdown code
    await db.close()

class SearchRequest(BaseModel):
    query: str

app = FastAPI(title="Enterprise RAG Platform", lifespan=lifespan)

@app.get("/")
async def health_check():
    return {"status": "running"}

@app.post("/ingest/")
async def ingest_document(
    file: UploadFile = File(...),
    conn = Depends(get_db_connection),
):
    tenant_id = await conn.fetchval("SELECT current_setting('app.current_tenant', 'true');")

    count = await process_file(file, tenant_id, conn)

    return {
        "status": "success",
        "chunks_inserted": count,
        "tenant_id": tenant_id
    }

@app.post("/search")
async def search_knowledge_base(
    request: SearchRequest,
    conn = Depends(get_db_connection),
):
    # get tenant id from the RLS setting
    tenant_id = await conn.fetchval("SELECT current_setting('app.current_tenant', 'true');")

    # run hybrid search
    results = await perform_hybrid_search(request.query, tenant_id, conn)

    return {
        "status": "success",
        "results_count": len(results),
        "result": results[:5]
    }

