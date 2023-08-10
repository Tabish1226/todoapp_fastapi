"""create address table

Revision ID: c5fd220c1a61
Revises: fe2684d466a2
Create Date: 2023-08-07 12:14:55.169130

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5fd220c1a61'
down_revision: Union[str, None] = 'fe2684d466a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'address',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('address1', sa.String(), nullable=False),
        sa.Column('address2', sa.String(), nullable=False),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('state', sa.String(), nullable=False),
        sa.Column('country', sa.String(), nullable=False),
        sa.Column('postalcode', sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('address')