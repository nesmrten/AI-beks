"""Create questions table

Revision ID: <some revision ID>
Revises: <previous revision ID>
Create Date: <date and time>

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'some revision ID'
down_revision = '<previous revision ID>'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('tag', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('questions')
