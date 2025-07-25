"""Change Tariff.name to JSON

Revision ID: d05f3eeeba4e
Revises: 08084ec8d138
Create Date: 2025-07-17 12:19:22.152240

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd05f3eeeba4e'
down_revision: Union[str, Sequence[str], None] = '08084ec8d138'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tariffs', 'name',
               existing_type=sa.VARCHAR(),
               type_=sa.JSON(),
               existing_nullable=False,
               postgresql_using="json_build_object('ru', name, 'en', name)")
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tariffs', 'name',
               existing_type=sa.JSON(),
               type_=sa.VARCHAR(),
               existing_nullable=False,
               postgresql_using="name->>'ru'")
    # ### end Alembic commands ###
