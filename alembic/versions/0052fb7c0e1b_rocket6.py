"""rocket6

Revision ID: 0052fb7c0e1b
Revises: 4fc62c8f6e0f
Create Date: 2025-03-12 11:56:08.322964

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0052fb7c0e1b'
down_revision: Union[str, None] = '4fc62c8f6e0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Rocket', 'time_start')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Rocket', sa.Column('time_start', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
