"""add tax fields to products and orders

Revision ID: 642f9e6d3f21
Revises: 75d6094268f7
Create Date: 2025-11-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '642f9e6d3f21'
down_revision: Union[str, None] = '75d6094268f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Products & variants tax rate
    op.add_column('products', sa.Column('tax_rate', sa.DECIMAL(5, 2), nullable=False, server_default='18.00'))
    op.add_column('product_variants', sa.Column('tax_rate', sa.DECIMAL(5, 2), nullable=False, server_default='18.00'))
    
    # Order summary tax columns
    op.add_column('orders', sa.Column('total_tax_amount', sa.DECIMAL(10, 2), nullable=False, server_default='0.00'))
    op.add_column('orders', sa.Column('grand_total_amount', sa.DECIMAL(10, 2), nullable=False, server_default='0.00'))
    
    # Order item level tax details
    op.add_column('order_items', sa.Column('tax_rate', sa.DECIMAL(5, 2), nullable=False, server_default='18.00'))
    op.add_column('order_items', sa.Column('tax_unit_amount', sa.DECIMAL(10, 2), nullable=False, server_default='0.00'))
    op.add_column('order_items', sa.Column('total_tax_amount', sa.DECIMAL(10, 2), nullable=False, server_default='0.00'))
    op.add_column('order_items', sa.Column('final_unit_price', sa.DECIMAL(10, 2), nullable=False, server_default='0.00'))
    op.add_column('order_items', sa.Column('total_final_amount', sa.DECIMAL(10, 2), nullable=False, server_default='0.00'))
    
    # Backfill summary values
    op.execute("""
        UPDATE order_items
        SET final_unit_price = customer_unit_price,
            total_final_amount = total_customer_amount
    """)
    op.execute("""
        UPDATE orders
        SET grand_total_amount = total_customer_amount
    """)


def downgrade() -> None:
    op.drop_column('order_items', 'total_final_amount')
    op.drop_column('order_items', 'final_unit_price')
    op.drop_column('order_items', 'total_tax_amount')
    op.drop_column('order_items', 'tax_unit_amount')
    op.drop_column('order_items', 'tax_rate')
    
    op.drop_column('orders', 'grand_total_amount')
    op.drop_column('orders', 'total_tax_amount')
    
    op.drop_column('product_variants', 'tax_rate')
    op.drop_column('products', 'tax_rate')

