"""Persist generated daily study plans."""

from alembic import op
import sqlalchemy as sa

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "learning_daily_study_plans",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("exam_type", sa.String(length=50), nullable=False),
        sa.Column("plan_date", sa.DateTime(), nullable=False),
        sa.Column("target_minutes", sa.Integer(), nullable=False),
        sa.Column("tasks", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "exam_type", "plan_date", name="uq_daily_plan_user_exam_date"),
    )
    op.create_index("ix_learning_daily_study_plans_user_id", "learning_daily_study_plans", ["user_id"])
    op.create_index("ix_learning_daily_study_plans_plan_date", "learning_daily_study_plans", ["plan_date"])


def downgrade() -> None:
    op.drop_index("ix_learning_daily_study_plans_plan_date", table_name="learning_daily_study_plans")
    op.drop_index("ix_learning_daily_study_plans_user_id", table_name="learning_daily_study_plans")
    op.drop_table("learning_daily_study_plans")
