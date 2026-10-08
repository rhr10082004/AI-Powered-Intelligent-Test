"""Add the durable learner activity and points ledger."""

from alembic import op
import sqlalchemy as sa

revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "learning_activity_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("event_key", sa.String(length=160), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("section", sa.String(length=50), nullable=True),
        sa.Column("reference_id", sa.String(length=36), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "event_key", name="uq_activity_user_event_key"),
    )
    op.create_index("ix_learning_activity_events_user_id", "learning_activity_events", ["user_id"])
    op.create_index("ix_learning_activity_events_event_type", "learning_activity_events", ["event_type"])
    op.create_index("ix_learning_activity_events_created_at", "learning_activity_events", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_learning_activity_events_created_at", table_name="learning_activity_events")
    op.drop_index("ix_learning_activity_events_event_type", table_name="learning_activity_events")
    op.drop_index("ix_learning_activity_events_user_id", table_name="learning_activity_events")
    op.drop_table("learning_activity_events")
