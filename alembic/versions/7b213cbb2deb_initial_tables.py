"""initial tables

Revision ID: 7b213cbb2deb
Revises:
Create Date: 2026-03-01 16:40:16.133085

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7b213cbb2deb"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create storage_units, scan_sessions and file_records tables."""
    op.create_table(
        "storage_units",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("alias", sa.String(100), nullable=False),
        sa.Column("unit_type", sa.String(50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("alias"),
    )

    op.create_table(
        "scan_sessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("storage_unit_id", sa.Integer(), nullable=False),
        sa.Column("root_path", sa.Text(), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_files", sa.Integer(), nullable=True),
        sa.Column("total_errors", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["storage_unit_id"], ["storage_units.id"]),
    )

    op.create_table(
        "file_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("scan_session_id", sa.Integer(), nullable=False),
        sa.Column("full_path", sa.Text(), nullable=False),
        sa.Column("file_name", sa.String(500), nullable=False),
        sa.Column("extension", sa.String(20), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("file_hash", sa.String(128), nullable=True),
        sa.Column("hash_algorithm", sa.String(20), nullable=True),
        sa.Column("created_at_os", sa.DateTime(timezone=True), nullable=True),
        sa.Column("modified_at_os", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "cataloged_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["scan_session_id"], ["scan_sessions.id"]),
        sa.UniqueConstraint("scan_session_id", "full_path", name="uq_session_path"),
    )

    # Indexes for common queries
    op.create_index("ix_file_records_file_hash", "file_records", ["file_hash"])
    op.create_index("ix_file_records_extension", "file_records", ["extension"])
    op.create_index("ix_file_records_size_bytes", "file_records", ["size_bytes"])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index("ix_file_records_size_bytes", table_name="file_records")
    op.drop_index("ix_file_records_extension", table_name="file_records")
    op.drop_index("ix_file_records_file_hash", table_name="file_records")
    op.drop_table("file_records")
    op.drop_table("scan_sessions")
    op.drop_table("storage_units")
