import asyncpg
from contextlib import asynccontextmanager
from fastapi import Request, HTTPException, Header
from app.config import settings

class Database:
    def __init__(self):
        self._pool = None
    
    async def connect(self):
        self.pool = await asyncpg.create_pool(dsn = settings.DATABASE_URL)
        print("Database pool created.")
    
    async def close(self):
        await self.pool.close()
        print("Database pool closed.")

db = Database()

# security dependency
# This function will be used as a dependency in FastAPI routes to get a database connection -> will be used in every API route
# It ensures that NO query runs without a tenant ID
async def get_db_connection(request: Request, x_tenant_id: str = Header(..., alias="X-Tenant-ID")):
    # simulate getting tenant_id from request headers (in real world, JWT token)
    tenant_id = x_tenant_id
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID is required")
    
    # aquire connection from pool
    async with db.pool.acquire() as conn:
        transaction = conn.transaction()
        await transaction.start()
        try:
            # Enforce security context
            await conn.execute(f"SET app.current_tenant = '{tenant_id}';")
            yield conn
            await transaction.commit()
        except Exception as e:
            await transaction.rollback()
            raise e

