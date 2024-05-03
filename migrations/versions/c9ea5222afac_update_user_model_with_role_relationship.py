"""Update User model with Role relationship

Revision ID: c9ea5222afac
Revises: 2ac29721a0c1
Create Date: 2023-11-26 21:53:58.150766

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9ea5222afac'
down_revision = '2ac29721a0c1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_temp')
    with op.batch_alter_table('user') as batch_op:
        batch_op.alter_column('role_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.create_foreign_key(None, 'role', ['role_id'], ['id'])
        batch_op.drop_column('role', use_alter=True, name='fk_user_role')


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(sa.Column('role', sa.VARCHAR(length=50), server_default=sa.text("'default_role_value'"), nullable=True))
        batch_op.drop_constraint('fk_role_user', type_='foreignkey')
        batch_op.alter_column('role_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    op.create_table('user_temp',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('username', sa.VARCHAR(length=255), nullable=False),
    sa.Column('email', sa.VARCHAR(length=255), nullable=False),
    sa.Column('password_hash', sa.VARCHAR(length=255), nullable=False),
    sa.Column('role_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], name='fk_role_user'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###