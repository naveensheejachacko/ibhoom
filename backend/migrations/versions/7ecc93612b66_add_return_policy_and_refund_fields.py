"""add_return_policy_and_refund_fields

Revision ID: 7ecc93612b66
Revises: 54d6cd0bc560
Create Date: 2025-11-26 00:05:07.464836

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ecc93612b66'
down_revision: Union[str, None] = '54d6cd0bc560'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add return policy fields to products table
    op.add_column('products', sa.Column('has_return_policy', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('products', sa.Column('return_period_days', sa.Integer(), nullable=False, server_default='7'))
    op.add_column('products', sa.Column('return_policy_description', sa.Text(), nullable=True))
    
    # Add refund tracking fields to orders table
    op.add_column('orders', sa.Column('return_requested_at', sa.DateTime(), nullable=True))
    op.add_column('orders', sa.Column('refund_amount', sa.DECIMAL(10, 2), nullable=True))
    op.add_column('orders', sa.Column('refund_date', sa.DateTime(), nullable=True))
    op.add_column('orders', sa.Column('refund_notes', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove fields from orders table
    op.drop_column('orders', 'refund_notes')
    op.drop_column('orders', 'refund_date')
    op.drop_column('orders', 'refund_amount')
    op.drop_column('orders', 'return_requested_at')
    
    # Remove fields from products table
    op.drop_column('products', 'return_policy_description')
    op.drop_column('products', 'return_period_days')
    op.drop_column('products', 'has_return_policy')
