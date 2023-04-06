"""create address table

Revision ID: 4eece7504943
Revises: 66a34aeb1219
Create Date: 2023-04-05 21:53:24.428508

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4eece7504943'
down_revision = '66a34aeb1219'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('address',
                    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('address1', sa.String(length=100), nullable=False),
                    sa.Column('address2', sa.String(length=100), nullable=True),
                    sa.Column('city', sa.String(length=50), nullable=False),
                    sa.Column('state', sa.String(), nullable=False),
                    sa.Column('country', sa.String(), nullable=False),
                    sa.Column('postalcode', sa.String(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('address')
