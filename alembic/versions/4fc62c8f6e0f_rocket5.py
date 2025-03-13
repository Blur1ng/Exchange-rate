"""rocket5

Revision ID: 4fc62c8f6e0f
Revises: b87c975d5f60
Create Date: 2025-03-11 07:12:55.463303

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4fc62c8f6e0f'
down_revision: Union[str, None] = 'b87c975d5f60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Rocket', sa.Column('time_take_profit', sa.DateTime(), nullable=True))
    op.drop_column('Rocket', 'time_start_start')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Rocket', sa.Column('time_start_start', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('Rocket', 'time_take_profit')
    # ### end Alembic commands ###
