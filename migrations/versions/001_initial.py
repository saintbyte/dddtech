"""initial migration with test data

Revision ID: 001
Revises:
Create Date: 2026-07-09
"""
from datetime import datetime
from hashlib import sha256

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("balance", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_accounts_user_id"), "accounts", ["user_id"], unique=False)

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("transaction_id", sa.String(length=255), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transaction_id"),
    )
    op.create_index(op.f("ix_payments_transaction_id"), "payments", ["transaction_id"], unique=True)

    op.create_foreign_key("fk_accounts_user_id", "accounts", "users", ["user_id"], ["id"], ondelete="CASCADE")
    op.create_foreign_key("fk_payments_account_id", "payments", "accounts", ["account_id"], ["id"], ondelete="CASCADE")

    from app.auth import hash_password

    user_hash = hash_password("user123")
    admin_hash = hash_password("admin123")

    op.execute(
        text(
            f"""INSERT INTO users (email, password_hash, full_name, is_admin, created_at)
            VALUES (
                'user@example.com',
                '{user_hash}',
                'Test User',
                false,
                '{datetime.utcnow().isoformat()}'
            )"""
        )
    )
    op.execute(
        text(
            f"""INSERT INTO users (email, password_hash, full_name, is_admin, created_at)
            VALUES (
                'admin@example.com',
                '{admin_hash}',
                'Test Admin',
                true,
                '{datetime.utcnow().isoformat()}'
            )"""
        )
    )
    op.execute(
        text(
            f"""INSERT INTO accounts (user_id, balance, created_at)
            VALUES (1, 1000.00, '{datetime.utcnow().isoformat()}')"""
        )
    )


def downgrade():
    op.drop_table("payments")
    op.drop_table("accounts")
    op.drop_table("users")
