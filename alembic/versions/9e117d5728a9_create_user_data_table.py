"""Create User_data table

Revision ID: 9e117d5728a9
Revises: ba570dbc763b
Create Date: 2025-01-25 14:55:29.469598
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9e117d5728a9'
down_revision = 'ba570dbc763b'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Создание таблицы User_data
    op.create_table(
        'User_data',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('username', sa.String(length=50), unique=True, nullable=False),
        sa.Column('password', sa.String(length=100), nullable=False)
    )

def downgrade() -> None:
    # Удаление таблицы при откате миграции
    op.drop_table('User_data')
