"""create_metric_sort_table

Revision ID: 82d43584a2b7
Revises: f0c93c1a27a4
Create Date: 2022-08-01 11:28:23.696759

"""
from utils.connection import create_db_engine, create_db_session


# revision identifiers, used by Alembic.
revision = "82d43584a2b7"
down_revision = "f0c93c1a27a4"
branch_labels = None
depends_on = None


def upgrade():
    engine = create_db_engine()
    session = create_db_session(engine)

    query = """
    CREATE TABLE IF NOT EXISTS metric_sort (
        id VARCHAR(36) PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        sort_value NUMERIC UNIQUE NOT NULL
    );
    """

    session.execute(query)
    session.commit()


def downgrade():
    pass
