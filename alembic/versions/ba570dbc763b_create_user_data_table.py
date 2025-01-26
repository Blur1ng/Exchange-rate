"""Create User_data table

Revision ID: ba570dbc763b
Revises: 
Create Date: 2025-01-25 13:53:24.231904
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'ba570dbc763b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создание таблицы User_data
    op.create_table(
        'User_data',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password', sa.String(length=100), nullable=False),
    )


def downgrade() -> None:
    # Удаление таблицы User_data при откате миграции
    op.drop_table('User_data')
