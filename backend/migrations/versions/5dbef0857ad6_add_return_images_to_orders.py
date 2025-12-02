"""add_return_images_to_orders

Revision ID: 5dbef0857ad6
Revises: e302a5ac438d
Create Date: 2025-11-29 16:05:54.891908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5dbef0857ad6'
down_revision: Union[str, None] = 'e302a5ac438d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add return_images column to store JSON array of image URLs
    op.add_column('orders', sa.Column('return_images', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('orders', 'return_images')
