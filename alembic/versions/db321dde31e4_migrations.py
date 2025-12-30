"""migrations

Revision ID: db321dde31e4
Revises: 6c8b9ba84c85
Create Date: 2025-12-24 18:01:24.463124

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db321dde31e4'
down_revision: Union[str, Sequence[str], None] = '6c8b9ba84c85'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_column('model_professional', 'experience_level')
    op.drop_column('model_professional', 'availability')


def downgrade():
    op.add_column(
        'model_professional',
        sa.Column('experience_level', sa.Enum('BEGINNER', 'INTERMEDIATE', 'EXPERT', name='experiencelevelenum'), nullable=True)
    )
    op.add_column(
        'model_professional',
        sa.Column('availability', sa.ARRAY(sa.String()), nullable=True)
    )