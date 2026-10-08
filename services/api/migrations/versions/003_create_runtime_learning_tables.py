"""Create the prefixed learning tables used by the active ORM models.

Revision ID: 003
Revises: 002
"""

from alembic import op

from services.api.models_phase2_isolated import BasePhase2


revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None

# These tables were introduced after revision 003; keep metadata-driven creation
# bounded so each is created only by its own migration.
_REVISION_004_TABLES = {
    "learning_tutor_conversations",
    "learning_tutor_messages",
    "learning_writing_submissions",
    "learning_grammar_attempts",
    "auth_action_tokens",
    "learning_daily_study_plans",
    "learning_activity_events",
}


def _revision_tables():
    return [table for table in BasePhase2.metadata.sorted_tables if table.name not in _REVISION_004_TABLES]


def upgrade() -> None:
    """Create the runtime learning tables that belong to revision 003."""
    BasePhase2.metadata.create_all(
        bind=op.get_bind(),
        tables=_revision_tables(),
        checkfirst=True,
    )


def downgrade() -> None:
    """Remove only the runtime learning tables introduced by revision 003."""
    BasePhase2.metadata.drop_all(
        bind=op.get_bind(),
        tables=_revision_tables(),
        checkfirst=True,
    )
