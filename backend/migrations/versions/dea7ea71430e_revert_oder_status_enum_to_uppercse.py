"""revert_oder_status_enum_to_uppercse

Revision ID: dea7ea71430e
Revises: 1967bb648bd9
Create Date: 2025-11-29 14:51:55.517109

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
    pass


def downgrade() -> None:
    pass
