"""ensure_order_status_enum_uppercase

Revision ID: e302a5ac438d
Revises: dea7ea71430e
Create Date: 2025-11-29 15:42:11.307396

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e302a5ac438d'
down_revision: Union[str, None] = 'dea7ea71430e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This migration ensures the orderstatus enum has uppercase values
    # It's idempotent and can be run multiple times safely
    
    # Step 1: Check if the column is already using the enum type
    # If it's VARCHAR, convert it temporarily to handle the conversion
    op.execute("""
        DO $$
        BEGIN
            -- Check if column is already VARCHAR (from a previous failed migration)
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'orders' 
                AND column_name = 'status' 
                AND data_type = 'character varying'
            ) THEN
                -- Column is already VARCHAR, proceed with updates
                NULL;
            ELSE
                -- Convert enum to VARCHAR temporarily
                ALTER TABLE orders ALTER COLUMN status TYPE VARCHAR(50);
            END IF;
        END $$;
    """)
    
    # Step 2: Update all existing data to uppercase format
    # Handle all possible current values (lowercase, mixed case, etc.)
    updates = [
        ("UPDATE orders SET status = 'PENDING' WHERE LOWER(status) = 'pending'"),
        ("UPDATE orders SET status = 'REJECTED' WHERE LOWER(status) = 'rejected'"),
        ("UPDATE orders SET status = 'PROCESSING' WHERE LOWER(status) = 'processing'"),
        ("UPDATE orders SET status = 'READY_FOR_DISPATCH' WHERE LOWER(REPLACE(status, ' ', '_')) = 'ready_for_dispatch' OR LOWER(status) = 'ready for dispatch'"),
        ("UPDATE orders SET status = 'DISPATCHED' WHERE LOWER(status) = 'dispatched'"),
        ("UPDATE orders SET status = 'DELIVERED' WHERE LOWER(status) = 'delivered'"),
        ("UPDATE orders SET status = 'CANCELLED' WHERE LOWER(status) = 'cancelled'"),
        ("UPDATE orders SET status = 'RETURN_REQUESTED' WHERE LOWER(REPLACE(status, ' ', '_')) = 'return_requested' OR LOWER(status) = 'return requested'"),
        ("UPDATE orders SET status = 'RETURN_APPROVED' WHERE LOWER(REPLACE(status, ' ', '_')) = 'return_approved' OR LOWER(status) = 'return approved'"),
        ("UPDATE orders SET status = 'RETURN_REJECTED' WHERE LOWER(REPLACE(status, ' ', '_')) = 'return_rejected' OR LOWER(status) = 'return rejected'"),
        ("UPDATE orders SET status = 'RETURN_PICKED_UP' WHERE LOWER(REPLACE(status, ' ', '_')) = 'return_picked_up' OR LOWER(status) = 'return picked up'"),
        ("UPDATE orders SET status = 'RETURN_RECEIVED' WHERE LOWER(REPLACE(status, ' ', '_')) = 'return_received' OR LOWER(status) = 'return received'"),
        ("UPDATE orders SET status = 'REFUND_PROCESSING' WHERE LOWER(REPLACE(status, ' ', '_')) = 'refund_processing' OR LOWER(status) = 'refund processing'"),
        ("UPDATE orders SET status = 'REFUND_COMPLETED' WHERE LOWER(REPLACE(status, ' ', '_')) = 'refund_completed' OR LOWER(status) = 'refund completed'"),
    ]
    
    for update in updates:
        op.execute(update)
    
    # Step 3: Drop the old enum type if it exists
    op.execute("DROP TYPE IF EXISTS orderstatus CASCADE")
    
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
    
    op.execute("DROP TYPE IF EXISTS orderstatus CASCADE")
    
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
