"""002_add_jobs_and_misconceptions — adds durable jobs table and indexes.

Revision ID: 002_add_jobs_and_misconceptions
Revises: 001_initial_schema
Create Date: 2026-10-15
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_add_jobs_and_misconceptions'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
      job_id              TEXT PRIMARY KEY,
      type                TEXT NOT NULL,
      payload_json        TEXT NOT NULL DEFAULT '{}',
      dedupe_key          TEXT UNIQUE,
      status              TEXT NOT NULL DEFAULT 'queued',
      attempts            INTEGER NOT NULL DEFAULT 0,
      max_attempts        INTEGER NOT NULL DEFAULT 6,
      next_run_at         BIGINT NOT NULL,
      lease_expires_at    BIGINT,
      last_error          TEXT,
      created_at          BIGINT NOT NULL,
      updated_at          BIGINT NOT NULL
    );
    """)

    op.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status_next_run ON jobs (status, next_run_at);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_jobs_lease_expires ON jobs (status, lease_expires_at);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS jobs;")
