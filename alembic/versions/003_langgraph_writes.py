"""003_langgraph_writes — adds langgraph_writes table for durable checkpointer writes.

Revision ID: 003_langgraph_writes
Revises: 002_add_jobs_and_misconceptions
Create Date: 2026-10-15
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003_langgraph_writes'
down_revision: Union[str, None] = '002_add_jobs_and_misconceptions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE IF NOT EXISTS langgraph_writes (
      thread_id           TEXT NOT NULL,
      checkpoint_ns       TEXT NOT NULL DEFAULT '',
      checkpoint_id       TEXT NOT NULL,
      task_id             TEXT NOT NULL,
      channel             TEXT NOT NULL,
      type                TEXT NOT NULL,
      blob                BYTEA,
      created_at          BIGINT NOT NULL,
      PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, channel)
    );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS langgraph_writes;")
