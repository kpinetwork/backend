"""add_column_in_time_period_table

Revision ID: ebd63e486d09
Revises: 8311d5b9014c
Create Date: 2022-12-23 06:27:28.374643

"""
from utils.connection import create_db_engine, create_db_session

# revision identifiers, used by Alembic.
revision = "ebd63e486d09"
down_revision = "8311d5b9014c"
branch_labels = None
depends_on = None


def upgrade():
    engine = create_db_engine()
    session = create_db_session(engine)

    query = """
            ALTER TABLE time_period
            ADD COLUMN period_name TEXT;
        """

    session.execute(query)
    session.commit()
    pass


def downgrade():
    pass
