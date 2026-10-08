"""Create private speaking practice history."""

from alembic import op
import sqlalchemy as sa

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "learning_speaking_submissions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("exam_type", sa.String(length=50), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("transcript", sa.Text(), nullable=False),
        sa.Column("estimated_score", sa.Float(), nullable=False),
        sa.Column("feedback", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_learning_speaking_submissions_user_id", "learning_speaking_submissions", ["user_id"])
    op.create_index("ix_learning_speaking_submissions_created_at", "learning_speaking_submissions", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_learning_speaking_submissions_created_at", table_name="learning_speaking_submissions")
    op.drop_index("ix_learning_speaking_submissions_user_id", table_name="learning_speaking_submissions")
    op.drop_table("learning_speaking_submissions")
