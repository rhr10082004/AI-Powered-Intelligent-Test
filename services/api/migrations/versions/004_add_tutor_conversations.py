"""Persist private AI tutor conversations and their messages."""

from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "learning_tutor_conversations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("exam_type", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_learning_tutor_conversations_user_id",
        "learning_tutor_conversations",
        ["user_id"],
    )
    op.create_table(
        "learning_tutor_messages",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("conversation_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["learning_tutor_conversations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_learning_tutor_messages_conversation_id",
        "learning_tutor_messages",
        ["conversation_id"],
    )
    op.create_index(
        "ix_learning_tutor_messages_created_at",
        "learning_tutor_messages",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_learning_tutor_messages_created_at", table_name="learning_tutor_messages")
    op.drop_index("ix_learning_tutor_messages_conversation_id", table_name="learning_tutor_messages")
    op.drop_table("learning_tutor_messages")
    op.drop_index("ix_learning_tutor_conversations_user_id", table_name="learning_tutor_conversations")
    op.drop_table("learning_tutor_conversations")
