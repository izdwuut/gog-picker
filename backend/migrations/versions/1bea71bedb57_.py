"""empty message

Revision ID: 1bea71bedb57
Revises: 00446b603815
Create Date: 2020-02-14 12:49:54.127086

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1bea71bedb57'
down_revision = '00446b603815'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reddit_users', sa.Column('age', sa.TIMESTAMP(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('reddit_users', 'age')
    # ### end Alembic commands ###