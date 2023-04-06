"""add apt num col

Revision ID: a43f842553cd
Revises: f7382925c6db
Create Date: 2023-04-05 22:38:07.665991

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a43f842553cd'
down_revision = 'f7382925c6db'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('address', sa.Column('apt_num', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('address', 'apt_num')
