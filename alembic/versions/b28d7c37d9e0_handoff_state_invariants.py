"""handoff state invariants

Revision ID: b28d7c37d9e0
Revises: f8d8b2676472
Create Date: 2025-12-30 17:21:13.223139

"""
from typing import Sequence, Union

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b28d7c37d9e0'
down_revision: Union[str, Sequence[str], None] = 'f8d8b2676472'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "handoff_state_receiving_party_check",
        "handoffs",
        "(state = 'active' AND receiving_party IS NULL) "
        "OR (state = 'pending' AND receiving_party IS NOT NULL)"
    )


def downgrade() -> None:
    op.drop_constraint(
        "handoff_state_receiving_party_check",
        "handoffs",
        type = "check"
    )
