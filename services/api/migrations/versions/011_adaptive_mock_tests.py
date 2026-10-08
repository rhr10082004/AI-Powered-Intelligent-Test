"""Create adaptive mock test attempts and score history."""

from alembic import op
import sqlalchemy as sa

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "learning_mock_test_attempts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("exam_type", sa.String(length=50), nullable=False),
        sa.Column("question_ids", sa.JSON(), nullable=False),
        sa.Column("adaptive_level", sa.String(length=30), nullable=False),
        sa.Column("responses", sa.JSON(), nullable=False),
        sa.Column("section_scores", sa.JSON(), nullable=False),
        sa.Column("topic_scores", sa.JSON(), nullable=False),
        sa.Column("question_count", sa.Integer(), nullable=False),
        sa.Column("correct_count", sa.Integer(), nullable=False),
        sa.Column("accuracy", sa.Float(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_learning_mock_test_attempts_user_id", "learning_mock_test_attempts", ["user_id"])
    op.create_index("ix_learning_mock_test_attempts_completed_at", "learning_mock_test_attempts", ["completed_at"])
    op.create_index("ix_learning_mock_test_attempts_created_at", "learning_mock_test_attempts", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_learning_mock_test_attempts_created_at", table_name="learning_mock_test_attempts")
    op.drop_index("ix_learning_mock_test_attempts_completed_at", table_name="learning_mock_test_attempts")
    op.drop_index("ix_learning_mock_test_attempts_user_id", table_name="learning_mock_test_attempts")
    op.drop_table("learning_mock_test_attempts")
