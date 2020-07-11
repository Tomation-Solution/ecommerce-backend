"""empty message

Revision ID: d65354c88b40
Revises: 
Create Date: 2020-07-11 15:26:09.218431

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd65354c88b40'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'categories', ['category_name'])
    op.alter_column('order_details', 'order_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.alter_column('order_details', 'product_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.add_column('products', sa.Column('description', sa.Text(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('products', 'description')
    op.alter_column('order_details', 'product_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.alter_column('order_details', 'order_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.drop_constraint(None, 'categories', type_='unique')
    # ### end Alembic commands ###