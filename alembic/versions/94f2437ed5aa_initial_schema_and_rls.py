"""initial_schema_and_rls

Revision ID: 94f2437ed5aa
Revises: 
Create Date: 2025-12-28 11:55:18.885812

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '94f2437ed5aa'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable Extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # 2. Create Tenants Table
    op.create_table(
        'tenants',
        sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), primary_key=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'))
    )

    # 3. Create Documents Table
    op.create_table(
        'documents',
        sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), primary_key=True),
        sa.Column('tenant_id', sa.UUID(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', sa.TEXT(), nullable=True), # We use TEXT placeholder for vector initially to avoid SQLAlchemy issues, then cast it
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'))
    )
    
    # 3b. Fix the vector column type manually
    # SQLAlchemy doesn't strictly know 'VECTOR' type by default unless we import pgvector, 
    # so we use raw SQL to alter it to the correct type.
    op.execute('ALTER TABLE documents ALTER COLUMN embedding TYPE vector(1536) USING embedding::vector(1536)')

    # 4. Add the Generated Column for Hybrid Search (TSVECTOR)
    op.execute("""
        ALTER TABLE documents 
        ADD COLUMN search_vector TSVECTOR 
        GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
    """)

    # 5. Create Indexes
    op.execute('CREATE INDEX idx_documents_search ON documents USING GIN(search_vector)')
    op.execute('CREATE INDEX idx_documents_embedding ON documents USING hnsw (embedding vector_cosine_ops)')

    # 6. Setup RLS (The Fortress)
    op.execute('ALTER TABLE documents ENABLE ROW LEVEL SECURITY')
    op.execute("""
        CREATE POLICY tenant_isolation_policy ON documents
        USING (tenant_id::text = current_setting('app.current_tenant', true))
    """)
    op.execute('ALTER TABLE documents FORCE ROW LEVEL SECURITY')

    # 7. Create App User (Idempotent check)
    op.execute("""
        DO
        $do$
        BEGIN
           IF NOT EXISTS (
              SELECT FROM pg_catalog.pg_roles
              WHERE  rolname = 'app_user') THEN
              CREATE ROLE app_user LOGIN PASSWORD 'app_password';
           END IF;
        END
        $do$;
    """)
    op.execute('GRANT CONNECT ON DATABASE rag_db TO app_user')
    op.execute('GRANT USAGE ON SCHEMA public TO app_user')
    op.execute('GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user')
    op.execute('GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_user')


def downgrade() -> None:
    # Undo everything in reverse order
    op.execute('DROP POLICY IF EXISTS tenant_isolation_policy ON documents')
    op.execute('ALTER TABLE documents DISABLE ROW LEVEL SECURITY')
    op.drop_table('documents')
    op.drop_table('tenants')
    # We typically don't drop the app_user or extensions in a downgrade 
    # as other tables might use them, but for this project, we can leave them.
