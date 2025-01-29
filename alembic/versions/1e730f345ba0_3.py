"""3

Revision ID: 1e730f345ba0
Revises: 6f21d1bd6d39
Create Date: 2025-01-29 12:54:09.182441

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e730f345ba0'
down_revision: Union[str, None] = '6f21d1bd6d39'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Trade_Result', sa.Column('end_price', sa.Float(), nullable=True))
    op.drop_column('Trade_data', 'end_price')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Trade_data', sa.Column('end_price', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.drop_column('Trade_Result', 'end_price')
    # ### end Alembic commands ###
