"""Add storage_path with unique constraint to Document

Revision ID: a1b2c3d4e5f6
Revises: c704c0199d6c

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
# IMPORTANT: Replace 'a1b2c3d4e5f6' with the actual revision ID from your filename
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "c704c0199d6c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # This is the correct, manually-adjusted batch operation for SQLite.
    with op.batch_alter_table("documents", schema=None) as batch_op:
        # Add the column. Setting a server_default is crucial for existing tables.
        batch_op.add_column(
            sa.Column(
                "storage_path", sa.String(length=512), nullable=False, server_default=""
            )
        )

        # Now, create the named unique constraint within the same batch.
        batch_op.create_unique_constraint("uq_documents_storage_path", ["storage_path"])


def downgrade() -> None:
    """Downgrade schema."""
    # The downgrade operation is the reverse.
    with op.batch_alter_table("documents", schema=None) as batch_op:
        # First, drop the named constraint.
        batch_op.drop_constraint("uq_documents_storage_path", type_="unique")

        # Then, drop the column.
        batch_op.drop_column("storage_path")
