"""remove experience_level and availability from model_professional

Revision ID: d36a53ba88c2
Revises: db321dde31e4
Create Date: 2025-12-24 18:31:03.931349

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd36a53ba88c2'
down_revision: Union[str, Sequence[str], None] = 'db321dde31e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
