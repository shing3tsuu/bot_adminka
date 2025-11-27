"""add_is_approved_to_users

Revision ID: e122ed0a5f77
Revises: 0d563507f2eb
Create Date: 2025-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e122ed0a5f77'
down_revision = '0d563507f2eb'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('users',
        sa.Column('is_approved', sa.Boolean(), nullable=False, server_default='false')
    )

def downgrade() -> None:
    op.drop_column('users', 'is_approved')
