"""add_organization_and_created_at

Revision ID: c25048bb513e
Revises: e122ed0a5f77
Create Date: 2025-11-27 19:58:35.968918

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'c25048bb513e'
down_revision = 'e122ed0a5f77'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users',
        sa.Column('organization', sa.String(length=100), nullable=True)
    )

    op.add_column('posts',
        sa.Column('created_at', sa.DateTime(), nullable=True)
    )

def downgrade() -> None:
    op.drop_column('posts', 'created_at')
    op.drop_column('users', 'organization')
