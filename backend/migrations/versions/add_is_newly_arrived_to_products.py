"""add_is_newly_arrived_to_products

Revision ID: add_newly_arrived
Revises: 5dbef0857ad6
Create Date: 2025-11-29 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_newly_arrived'
down_revision: Union[str, None] = '5dbef0857ad6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_newly_arrived column to products table
    op.add_column('products', sa.Column('is_newly_arrived', sa.Boolean(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('products', 'is_newly_arrived')



