"""recreate model_professional table

Revision ID: e6b53a4e0141
Revises: d36a53ba88c2
Create Date: 2025-12-24 18:35:43.709002

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6b53a4e0141'
down_revision: Union[str, Sequence[str], None] = 'd36a53ba88c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_table("model_professional")

    op.create_table(
        "model_professional",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.UUID, server_default=sa.text("gen_random_uuid()"), nullable=False, unique=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),

        sa.Column("professional_experience", sa.Boolean, server_default=sa.text("false")),
        sa.Column("experience_details", sa.String(255)),

        sa.Column("languages", sa.ARRAY(sa.String())),
        sa.Column("skills", sa.ARRAY(sa.String())),
        sa.Column("interested_categories", sa.ARRAY(sa.String())),
        sa.Column("willing_to_travel", sa.Boolean, server_default=sa.text("false")),

        sa.Column("created_by", sa.Integer),
        sa.Column("updated_by", sa.Integer),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("now()")),
    )


def downgrade():
    op.drop_table("model_professional")
