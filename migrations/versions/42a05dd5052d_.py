"""empty message

Revision ID: 42a05dd5052d
Revises: 424c7730ff8f
Create Date: 2020-07-12 11:56:02.479272

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '42a05dd5052d'
down_revision = '424c7730ff8f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('order_details', 'order_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.alter_column('order_details', 'product_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.add_column('orders', sa.Column('address_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'orders', 'address', ['address_id'], ['address_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'orders', type_='foreignkey')
    op.drop_column('orders', 'address_id')
    op.alter_column('order_details', 'product_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.alter_column('order_details', 'order_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    # ### end Alembic commands ###
