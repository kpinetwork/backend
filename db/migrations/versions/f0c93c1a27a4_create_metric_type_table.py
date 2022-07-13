"""create_metric_type_table

Revision ID: f0c93c1a27a4
Revises: 051ca978f7ec
Create Date: 2022-07-13 06:19:55.078233

"""
from utils.connection import create_db_engine, create_db_session


# revision identifiers, used by Alembic.
revision = "f0c93c1a27a4"
down_revision = "051ca978f7ec"
branch_labels = None
depends_on = None


def upgrade():
    engine = create_db_engine()
    session = create_db_session(engine)

    query = """
    CREATE TABLE IF NOT EXISTS metric_types (
        id VARCHAR(36) PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
    );
    """

    session.execute(query)
    session.commit()


def downgrade():
    pass
