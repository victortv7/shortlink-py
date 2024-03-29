"""Create urls table

Revision ID: b21ba5023297
Revises: 
Create Date: 2024-03-29 17:53:28.695996

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b21ba5023297'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('urls',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('long_url', sa.String(), nullable=False),
    sa.Column('access_count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_urls_id'), 'urls', ['id'], unique=False)
    op.execute("SELECT setval('urls_id_seq', 100000000, false)")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_urls_id'), table_name='urls')
    op.drop_table('urls')
    # ### end Alembic commands ###
