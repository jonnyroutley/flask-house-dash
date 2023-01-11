"""empty message

Revision ID: fae76b6d1981
Revises: 
Create Date: 2023-01-10 22:54:28.883035

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fae76b6d1981'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bins',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('colour', sa.String(length=200), nullable=False),
    sa.Column('collection_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('shopping_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('quantity', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shopping_item', schema=None) as batch_op:
        batch_op.drop_column('quantity')

    op.drop_table('bins')
    # ### end Alembic commands ###
