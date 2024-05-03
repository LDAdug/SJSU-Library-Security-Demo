"""empty message

Revision ID: 2ac29721a0c1
Revises: d82827352fa2
Create Date: 2023-11-26 21:15:14.093005

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ac29721a0c1'
down_revision = 'd82827352fa2'
branch_labels = None
depends_on = None

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import text


Base = declarative_base()

class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    role_id = Column(Integer, ForeignKey('role.id'))

def upgrade():
    # Check if the 'user_temp' table already exists
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    user_temp_exists = 'user_temp' in inspector.get_table_names()

    if not user_temp_exists:
        # Create a new 'user_temp' table with the desired schema
        op.create_table('user_temp',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('username', sa.String(length=255), nullable=False),
            sa.Column('email', sa.String(length=255), nullable=False),
            sa.Column('password_hash', sa.String(length=255), nullable=False),
            sa.Column('role_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['role_id'], ['role.id'], name='fk_role_user'),
            sa.PrimaryKeyConstraint('id')
        )

        # Specify column names explicitly in the INSERT statement
        op.execute('INSERT INTO user_temp (id, username, email, password_hash, role_id) SELECT id, username, email, password_hash, role_id FROM user WHERE role_id IS NOT NULL')

        # Drop the old 'user' table
        op.drop_table('user')

        # Rename the 'user_temp' table to 'user'
        op.rename_table('user_temp', 'user')



def downgrade():
    # Connect to the database
    engine = create_engine("sqlite:///your_database.db")
    session = Session(engine)

    # Drop the foreign key constraint
    session.execute(text('PRAGMA foreign_keys=off'))
    session.commit()

    # Create a new role table
    Base.metadata.create_all(bind=engine)

    # Copy data from old role to new role
    session.execute(Role.__table__.insert().from_select(['id', 'name'], session.query(Role.id, Role.name)))

    # Copy data from old user to new user
    session.execute(User.__table__.insert().from_select(['id', 'username', 'role_id'], session.query(User.id, User.username, User.role_id)))

    # Drop the old user table
    session.execute(text('DROP TABLE user'))

    # Rename the new role table to the original name
    session.execute(text('ALTER TABLE role RENAME TO user'))

    # Commit the changes
    session.commit()