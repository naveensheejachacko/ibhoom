"""revert_oder_status_enum_to_uppercse

Revision ID: dea7ea71430e
Revises: 1967bb648bd9
Create Date: 2025-11-29 09:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dea7ea71430e'
down_revision: Union[str, None] = '1967bb648bd9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Alter the status column to VARCHAR temporarily
    op.execute("ALTER TABLE orders ALTER COLUMN status TYPE VARCHAR(50)")
    
    # Step 2: Update existing data - convert lowercase spaces to uppercase underscores
    # Map old values to new values
    updates = [
        ("UPDATE orders SET status = 'PENDING' WHERE status = 'pending'"),
        ("UPDATE orders SET status = 'REJECTED' WHERE status = 'rejected'"),
        ("UPDATE orders SET status = 'PROCESSING' WHERE status = 'processing'"),
        ("UPDATE orders SET status = 'READY_FOR_DISPATCH' WHERE status = 'ready for dispatch'"),
        ("UPDATE orders SET status = 'DISPATCHED' WHERE status = 'dispatched'"),
        ("UPDATE orders SET status = 'DELIVERED' WHERE status = 'delivered'"),
        ("UPDATE orders SET status = 'CANCELLED' WHERE status = 'cancelled'"),
        ("UPDATE orders SET status = 'RETURN_REQUESTED' WHERE status = 'return requested'"),
        ("UPDATE orders SET status = 'RETURN_APPROVED' WHERE status = 'return approved'"),
        ("UPDATE orders SET status = 'RETURN_REJECTED' WHERE status = 'return rejected'"),
        ("UPDATE orders SET status = 'RETURN_PICKED_UP' WHERE status = 'return picked up'"),
        ("UPDATE orders SET status = 'RETURN_RECEIVED' WHERE status = 'return received'"),
        ("UPDATE orders SET status = 'REFUND_PROCESSING' WHERE status = 'refund processing'"),
        ("UPDATE orders SET status = 'REFUND_COMPLETED' WHERE status = 'refund completed'"),
    ]
    
    for update in updates:
        op.execute(update)
    
    # Step 3: Drop the old enum type
    op.execute("DROP TYPE IF EXISTS orderstatus")
    
    # Step 4: Create new enum type with uppercase values
    op.execute("""
        CREATE TYPE orderstatus AS ENUM (
            'PENDING',
            'REJECTED',
            'PROCESSING',
            'READY_FOR_DISPATCH',
            'DISPATCHED',
            'DELIVERED',
            'CANCELLED',
            'RETURN_REQUESTED',
            'RETURN_APPROVED',
            'RETURN_REJECTED',
            'RETURN_PICKED_UP',
            'RETURN_RECEIVED',
            'REFUND_PROCESSING',
            'REFUND_COMPLETED'
        )
    """)
    
    # Step 5: Convert the column back to enum type
    op.execute("ALTER TABLE orders ALTER COLUMN status TYPE orderstatus USING status::orderstatus")


def downgrade() -> None:
    # Reverse the process - convert back to lowercase
    op.execute("ALTER TABLE orders ALTER COLUMN status TYPE VARCHAR(50)")
    
    # Convert back to lowercase format
    updates = [
        ("UPDATE orders SET status = 'pending' WHERE status = 'PENDING'"),
        ("UPDATE orders SET status = 'rejected' WHERE status = 'REJECTED'"),
        ("UPDATE orders SET status = 'processing' WHERE status = 'PROCESSING'"),
        ("UPDATE orders SET status = 'ready for dispatch' WHERE status = 'READY_FOR_DISPATCH'"),
        ("UPDATE orders SET status = 'dispatched' WHERE status = 'DISPATCHED'"),
        ("UPDATE orders SET status = 'delivered' WHERE status = 'DELIVERED'"),
        ("UPDATE orders SET status = 'cancelled' WHERE status = 'CANCELLED'"),
        ("UPDATE orders SET status = 'return requested' WHERE status = 'RETURN_REQUESTED'"),
        ("UPDATE orders SET status = 'return approved' WHERE status = 'RETURN_APPROVED'"),
        ("UPDATE orders SET status = 'return rejected' WHERE status = 'RETURN_REJECTED'"),
        ("UPDATE orders SET status = 'return picked up' WHERE status = 'RETURN_PICKED_UP'"),
        ("UPDATE orders SET status = 'return received' WHERE status = 'RETURN_RECEIVED'"),
        ("UPDATE orders SET status = 'refund processing' WHERE status = 'REFUND_PROCESSING'"),
        ("UPDATE orders SET status = 'refund completed' WHERE status = 'REFUND_COMPLETED'"),
    ]
    
    for update in updates:
        op.execute(update)
    
    op.execute("DROP TYPE IF EXISTS orderstatus")
    
    # Recreate old enum with lowercase values
    op.execute("""
        CREATE TYPE orderstatus AS ENUM (
            'pending',
            'rejected',
            'processing',
            'ready for dispatch',
            'dispatched',
            'delivered',
            'cancelled',
            'return requested',
            'return approved',
            'return rejected',
            'return picked up',
            'return received',
            'refund processing',
            'refund completed'
        )
    """)
    
    op.execute("ALTER TABLE orders ALTER COLUMN status TYPE orderstatus USING status::orderstatus")
