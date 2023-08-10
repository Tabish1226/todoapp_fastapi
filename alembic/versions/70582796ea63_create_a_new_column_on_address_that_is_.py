"""create a new column on address that is called 'apt_num'

Revision ID: 70582796ea63
Revises: c0dc0d7ffd92
Create Date: 2023-08-08 16:40:59.396177

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70582796ea63'
down_revision: Union[str, None] = 'c0dc0d7ffd92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('address', sa.Column('apt_num', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('address', 'apt_num')
