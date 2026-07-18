"""Phase 2 database migration - Create learning content tables.

Revision ID: 002
Revises: 001
Create Date: 2026-01-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create Phase 2 tables."""
    
    # Create questions table
    op.create_table(
        'questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('exam_type', sa.String(50), nullable=False),
        sa.Column('section', sa.String(50), nullable=False),
        sa.Column('subsection', sa.String(100), nullable=True),
        sa.Column('question_type', sa.String(50), nullable=False),
        sa.Column('difficulty', sa.String(50), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('time_limit', sa.Integer(), nullable=True),
        sa.Column('audio_url', sa.String(500), nullable=True),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('source', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('exam_type', 'section', 'text', name='uq_question_unique')
    )
    
    # Create answers table
    op.create_table(
        'answers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create user_answers table
    op.create_table(
        'user_answers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('answer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_text_answer', sa.Text(), nullable=True),
        sa.Column('is_correct', sa.Boolean(), nullable=True),
        sa.Column('time_taken', sa.Integer(), nullable=True),
        sa.Column('attempts', sa.Integer(), nullable=False),
        sa.Column('review_count', sa.Integer(), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['answer_id'], ['answers.id'], ),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create passages table
    op.create_table(
        'passages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('word_count', sa.Integer(), nullable=False),
        sa.Column('exam_type', sa.String(50), nullable=False),
        sa.Column('difficulty', sa.String(50), nullable=False),
        sa.Column('topic', sa.String(255), nullable=True),
        sa.Column('source', sa.String(255), nullable=True),
        sa.Column('time_limit', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create listening_tracks table
    op.create_table(
        'listening_tracks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('audio_url', sa.String(500), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=False),
        sa.Column('transcript', sa.Text(), nullable=True),
        sa.Column('exam_type', sa.String(50), nullable=False),
        sa.Column('difficulty', sa.String(50), nullable=False),
        sa.Column('topic', sa.String(255), nullable=True),
        sa.Column('source', sa.String(255), nullable=True),
        sa.Column('accent', sa.String(50), nullable=True),
        sa.Column('play_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create vocabulary_words table
    op.create_table(
        'vocabulary_words',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('word', sa.String(255), nullable=False),
        sa.Column('definition', sa.Text(), nullable=False),
        sa.Column('part_of_speech', sa.String(50), nullable=False),
        sa.Column('pronunciation', sa.String(255), nullable=True),
        sa.Column('examples', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('synonyms', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('antonyms', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('exam_type', sa.String(50), nullable=False),
        sa.Column('difficulty', sa.String(50), nullable=False),
        sa.Column('frequency', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('word')
    )
    
    # Create user_vocabulary table
    op.create_table(
        'user_vocabulary',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('word_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('proficiency_level', sa.Integer(), nullable=False),
        sa.Column('review_count', sa.Integer(), nullable=False),
        sa.Column('last_reviewed', sa.DateTime(), nullable=True),
        sa.Column('next_review', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['word_id'], ['vocabulary_words.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create grammar_topics table
    op.create_table(
        'grammar_topics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('topic_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('examples', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('exam_type', sa.String(50), nullable=False),
        sa.Column('difficulty', sa.String(50), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('topic_name')
    )
    
    # Create grammar_exercises table
    op.create_table(
        'grammar_exercises',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('topic_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sentence', sa.Text(), nullable=False),
        sa.Column('correct_form', sa.String(500), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('difficulty', sa.String(50), nullable=False),
        sa.Column('hint', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['topic_id'], ['grammar_topics.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create study_sessions table
    op.create_table(
        'study_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('exam_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('section', sa.String(50), nullable=False),
        sa.Column('session_date', sa.DateTime(), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=False),
        sa.Column('questions_attempted', sa.Integer(), nullable=False),
        sa.Column('questions_correct', sa.Integer(), nullable=False),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['exam_id'], ['user_exams.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'exam_id', 'session_date', name='uq_study_session')
    )
    
    # Create user_progress table
    op.create_table(
        'user_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('exam_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('section', sa.String(50), nullable=False),
        sa.Column('total_questions', sa.Integer(), nullable=False),
        sa.Column('correct_answers', sa.Integer(), nullable=False),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('average_score', sa.Float(), nullable=True),
        sa.Column('last_practiced', sa.DateTime(), nullable=True),
        sa.Column('study_streak', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['exam_id'], ['user_exams.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'exam_id')
    )
    
    # Create indexes for performance
    op.create_index('ix_questions_exam_type', 'questions', ['exam_type'])
    op.create_index('ix_questions_section', 'questions', ['section'])
    op.create_index('ix_questions_difficulty', 'questions', ['difficulty'])
    op.create_index('ix_user_answers_user_id', 'user_answers', ['user_id'])
    op.create_index('ix_user_answers_question_id', 'user_answers', ['question_id'])
    op.create_index('ix_passages_exam_type', 'passages', ['exam_type'])
    op.create_index('ix_listening_tracks_exam_type', 'listening_tracks', ['exam_type'])
    op.create_index('ix_vocabulary_words_exam_type', 'vocabulary_words', ['exam_type'])
    op.create_index('ix_user_vocabulary_user_id', 'user_vocabulary', ['user_id'])
    op.create_index('ix_grammar_topics_exam_type', 'grammar_topics', ['exam_type'])
    op.create_index('ix_study_sessions_user_id', 'study_sessions', ['user_id'])
    op.create_index('ix_user_progress_user_id', 'user_progress', ['user_id'])


def downgrade() -> None:
    """Drop Phase 2 tables."""
    
    # Drop indexes
    op.drop_index('ix_user_progress_user_id', table_name='user_progress')
    op.drop_index('ix_study_sessions_user_id', table_name='study_sessions')
    op.drop_index('ix_grammar_topics_exam_type', table_name='grammar_topics')
    op.drop_index('ix_user_vocabulary_user_id', table_name='user_vocabulary')
    op.drop_index('ix_vocabulary_words_exam_type', table_name='vocabulary_words')
    op.drop_index('ix_listening_tracks_exam_type', table_name='listening_tracks')
    op.drop_index('ix_passages_exam_type', table_name='passages')
    op.drop_index('ix_user_answers_question_id', table_name='user_answers')
    op.drop_index('ix_user_answers_user_id', table_name='user_answers')
    op.drop_index('ix_questions_difficulty', table_name='questions')
    op.drop_index('ix_questions_section', table_name='questions')
    op.drop_index('ix_questions_exam_type', table_name='questions')
    
    # Drop tables
    op.drop_table('user_progress')
    op.drop_table('study_sessions')
    op.drop_table('grammar_exercises')
    op.drop_table('grammar_topics')
    op.drop_table('user_vocabulary')
    op.drop_table('vocabulary_words')
    op.drop_table('listening_tracks')
    op.drop_table('passages')
    op.drop_table('user_answers')
    op.drop_table('answers')
    op.drop_table('questions')
