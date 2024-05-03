"""Add role_id column to User table

Revision ID: d82827352fa2
Revises: bdd95797965d
Create Date: 2023-11-26 20:15:20.578754

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd82827352fa2'
down_revision = 'bdd95797965d'
branch_labels = None
depends_on = None

def upgrade():
    # Create a temporary table with the new structure
    op.create_table(
        'user_temp',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('registration_date', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email'),
    )

    # Copy data from the old table to the new table
    op.execute("INSERT INTO user_temp (id, username, password_hash, email, registration_date, role_id) SELECT id, username, password_hash, email, registration_date, NULL FROM user")

    # Drop the old table and rename the new table
    op.drop_table('user')
    op.rename_table('user_temp', 'user')

def downgrade():
    # Create a temporary table with the old structure
    op.create_table(
        'user_temp',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('registration_date', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.CheckConstraint("role IN ('Admin', 'Member')", name="ck_user_role"),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email'),
    )

    # Copy data from the new table to the old table
    op.execute("INSERT INTO user_temp (id, username, password_hash, email, registration_date, role) SELECT id, username, password_hash, email, registration_date, 'Member' FROM user")

    # Drop the new table and rename the old table
    op.drop_table('user')
    op.rename_table('user_temp', 'user')



