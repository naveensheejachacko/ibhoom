"""Change product_images image_url to Text for base64 support

Revision ID: 7cc492186581
Revises: cf9eeb7a63aa
Create Date: 2025-11-05 21:25:38.653823

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7cc492186581'
down_revision: Union[str, None] = 'cf9eeb7a63aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Change image_url from VARCHAR(500) to TEXT to support base64-encoded images
    op.alter_column('product_images', 'image_url',
                   existing_type=sa.String(length=500),
                   type_=sa.Text(),
                   nullable=False)


def downgrade() -> None:
    # Revert back to VARCHAR(500) - note: this may truncate data if images are longer
    op.alter_column('product_images', 'image_url',
                   existing_type=sa.Text(),
                   type_=sa.String(length=500),
                   nullable=False)
