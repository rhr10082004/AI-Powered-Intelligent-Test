"""Create durable writing evaluation history."""

from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "learning_writing_submissions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("exam_type", sa.String(length=50), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("essay", sa.Text(), nullable=False),
        sa.Column("word_count", sa.Integer(), nullable=False),
        sa.Column("estimated_band", sa.Float(), nullable=False),
        sa.Column("evaluation_method", sa.String(length=20), nullable=False),
        sa.Column("feedback", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_learning_writing_submissions_user_id", "learning_writing_submissions", ["user_id"])
    op.create_index("ix_learning_writing_submissions_created_at", "learning_writing_submissions", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_learning_writing_submissions_created_at", table_name="learning_writing_submissions")
    op.drop_index("ix_learning_writing_submissions_user_id", table_name="learning_writing_submissions")
    op.drop_table("learning_writing_submissions")
