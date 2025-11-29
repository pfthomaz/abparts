"""add hybrid media storage

Revision ID: 20251129_hybrid_storage
Revises: 20251124_order_txn
Create Date: 2024-11-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251129_hybrid_storage'
down_revision = '20251124_order_txn'
branch_labels = None
depends_on = None


def upgrade():
    # Add binary image storage columns to existing tables
    op.add_column('users', sa.Column('profile_photo_data', sa.LargeBinary(), nullable=True))
    op.add_column('organizations', sa.Column('logo_data', sa.LargeBinary(), nullable=True))
    op.add_column('parts', sa.Column('image_data', postgresql.ARRAY(sa.LargeBinary()), nullable=True))
    
    # Create support_videos table
    op.create_table(
        'support_videos',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_size_mb', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('thumbnail_data', sa.LargeBinary(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False)
    )
    op.create_index('idx_support_videos_category', 'support_videos', ['category'])
    
    # Create part_videos table
    op.create_table(
        'part_videos',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('part_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('parts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('video_type', sa.String(50), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_size_mb', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('thumbnail_data', sa.LargeBinary(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False)
    )
    op.create_index('idx_part_videos_part_id', 'part_videos', ['part_id'])


def downgrade():
    # Drop video tables
    op.drop_index('idx_part_videos_part_id', table_name='part_videos')
    op.drop_table('part_videos')
    op.drop_index('idx_support_videos_category', table_name='support_videos')
    op.drop_table('support_videos')
    
    # Drop binary image columns
    op.drop_column('parts', 'image_data')
    op.drop_column('organizations', 'logo_data')
    op.drop_column('users', 'profile_photo_data')
