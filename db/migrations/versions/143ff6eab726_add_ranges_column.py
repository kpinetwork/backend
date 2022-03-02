"""add_ranges_column

Revision ID: 143ff6eab726
Revises: 0b49ea1746af
Create Date: 2022-03-02 11:22:28.445152

"""
from utils.connection import create_db_engine, create_db_session

# revision identifiers, used by Alembic.
revision = "143ff6eab726"
down_revision = "0b49ea1746af"
branch_labels = None
depends_on = None


def upgrade():
    engine = create_db_engine()
    session = create_db_session(engine)

    query = """
        CREATE TABLE IF NOT EXISTS value_range (
            id VARCHAR(36) PRIMARY KEY,
            label TEXT NOT NULL,
            min_value NUMERIC,
            max_value NUMERIC
        );
        """

    session.execute(query)
    session.commit()

    pass


def downgrade():
    pass
