"""Add protocol and checklist item translations

Revision ID: add_protocol_translations_06
Revises: 04_add_preferred_language
Create Date: 2024-12-11 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_protocol_translations_06'
down_revision = '04_add_preferred_language'
branch_labels = None
depends_on = None


def upgrade():
    # Add base_language column to maintenance_protocols
    op.add_column('maintenance_protocols', 
                  sa.Column('base_language', sa.String(5), nullable=False, server_default='en'))
    
    # Add base_language column to protocol_checklist_items
    op.add_column('protocol_checklist_items', 
                  sa.Column('base_language', sa.String(5), nullable=False, server_default='en'))
    
    # Create protocol_translations table
    op.create_table('protocol_translations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('protocol_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('language_code', sa.String(5), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['protocol_id'], ['maintenance_protocols.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('protocol_id', 'language_code', name='uq_protocol_translations_protocol_language')
    )
    
    # Create checklist_item_translations table
    op.create_table('checklist_item_translations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('checklist_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('language_code', sa.String(5), nullable=False),
        sa.Column('item_description', sa.Text(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('item_category', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['checklist_item_id'], ['protocol_checklist_items.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('checklist_item_id', 'language_code', name='uq_checklist_translations_item_language')
    )
    
    # Create indexes for better performance
    op.create_index('ix_protocol_translations_protocol_id', 'protocol_translations', ['protocol_id'])
    op.create_index('ix_protocol_translations_language_code', 'protocol_translations', ['language_code'])
    op.create_index('ix_checklist_translations_item_id', 'checklist_item_translations', ['checklist_item_id'])
    op.create_index('ix_checklist_translations_language_code', 'checklist_item_translations', ['language_code'])
    
    # Populate base language translations for existing protocols
    # This creates English translations from existing data
    op.execute("""
        INSERT INTO protocol_translations (protocol_id, language_code, name, description)
        SELECT id, 'en', name, description 
        FROM maintenance_protocols 
        WHERE name IS NOT NULL
    """)
    
    # Populate base language translations for existing checklist items
    op.execute("""
        INSERT INTO checklist_item_translations (checklist_item_id, language_code, item_description, notes, item_category)
        SELECT id, 'en', item_description, notes, item_category 
        FROM protocol_checklist_items 
        WHERE item_description IS NOT NULL
    """)


def downgrade():
    # Drop indexes
    op.drop_index('ix_checklist_translations_language_code', 'checklist_item_translations')
    op.drop_index('ix_checklist_translations_item_id', 'checklist_item_translations')
    op.drop_index('ix_protocol_translations_language_code', 'protocol_translations')
    op.drop_index('ix_protocol_translations_protocol_id', 'protocol_translations')
    
    # Drop tables
    op.drop_table('checklist_item_translations')
    op.drop_table('protocol_translations')
    
    # Remove base_language columns
    op.drop_column('protocol_checklist_items', 'base_language')
    op.drop_column('maintenance_protocols', 'base_language')