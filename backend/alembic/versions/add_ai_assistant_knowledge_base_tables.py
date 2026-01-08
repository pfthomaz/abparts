"""Add AI Assistant knowledge base tables

Revision ID: add_ai_knowledge_base
Revises: [current_head]
Create Date: 2025-01-08 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_ai_knowledge_base'
down_revision = 'a78bd1ac6e99'  # baseline_from_production_20251231
branch_labels = None
depends_on = None


def upgrade():
    # Create knowledge_documents table
    op.create_table('knowledge_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('document_type', sa.String(length=50), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False, server_default='en'),
        sa.Column('version', sa.String(length=20), nullable=False, server_default='1.0'),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('machine_models', postgresql.ARRAY(sa.Text()), nullable=True, server_default="'{}'"),
        sa.Column('tags', postgresql.ARRAY(sa.Text()), nullable=True, server_default="'{}'"),
        sa.Column('document_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default="'{}'"),
        sa.Column('chunk_count', sa.Integer(), nullable=True, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for knowledge_documents
    op.create_index('idx_knowledge_documents_type', 'knowledge_documents', ['document_type'])
    op.create_index('idx_knowledge_documents_language', 'knowledge_documents', ['language'])
    
    # Create document_chunks table (note: using document_chunks not knowledge_chunks)
    op.create_table('document_chunks',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['document_id'], ['knowledge_documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index for document_chunks
    op.create_index('idx_document_chunks_document_id', 'document_chunks', ['document_id'])


def downgrade():
    # Drop tables and indexes
    op.drop_index('idx_document_chunks_document_id', table_name='document_chunks')
    op.drop_table('document_chunks')
    op.drop_index('idx_knowledge_documents_language', table_name='knowledge_documents')
    op.drop_index('idx_knowledge_documents_type', table_name='knowledge_documents')
    op.drop_table('knowledge_documents')