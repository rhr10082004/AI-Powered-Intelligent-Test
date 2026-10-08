"""Persist grammar exercise attempts."""

from alembic import op
import sqlalchemy as sa

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "learning_grammar_attempts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("exercise_id", sa.String(length=36), nullable=False),
        sa.Column("user_answer", sa.String(length=500), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["exercise_id"], ["learning_grammar_exercises.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_learning_grammar_attempts_user_id", "learning_grammar_attempts", ["user_id"])
    op.create_index("ix_learning_grammar_attempts_exercise_id", "learning_grammar_attempts", ["exercise_id"])
    op.create_index("ix_learning_grammar_attempts_created_at", "learning_grammar_attempts", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_learning_grammar_attempts_created_at", table_name="learning_grammar_attempts")
    op.drop_index("ix_learning_grammar_attempts_exercise_id", table_name="learning_grammar_attempts")
    op.drop_index("ix_learning_grammar_attempts_user_id", table_name="learning_grammar_attempts")
    op.drop_table("learning_grammar_attempts")
