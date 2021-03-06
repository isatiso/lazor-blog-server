"""modify article add publish state

Revision ID: 8c8e9d2a678d
Revises: af057997da7a
Create Date: 2017-10-27 11:28:59.699535

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c8e9d2a678d'
down_revision = 'af057997da7a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('article', sa.Column('publish_status', sa.SmallInteger(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('article', 'publish_status')
    # ### end Alembic commands ###
