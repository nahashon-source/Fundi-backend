"""add fundi_marked_done to jobs

Revision ID: 5351fa71ce37
Revises: 7d70c1d238ed
Create Date: 2026-07-02 15:04:47.616617

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '5351fa71ce37'
down_revision: Union[str, None] = '7d70c1d238ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('jobs') as batch_op:
        batch_op.add_column(sa.Column('fundi_marked_done', sa.Boolean(), nullable=False, server_default='0'))
        batch_op.create_foreign_key('fk_jobs_fundi_id', 'fundi_profiles', ['fundi_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('jobs') as batch_op:
        batch_op.drop_constraint('fk_jobs_fundi_id', type_='foreignkey')
        batch_op.drop_column('fundi_marked_done')