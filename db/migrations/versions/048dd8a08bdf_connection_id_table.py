"""connection_id_table

Revision ID: 048dd8a08bdf
Revises: 80253de57d77
Create Date: 2022-04-26 09:55:17.516584

"""

from utils.connection import create_db_engine, create_db_session

# revision identifiers, used by Alembic.
revision = "048dd8a08bdf"
down_revision = "80253de57d77"
branch_labels = None
depends_on = None


def upgrade():
    engine = create_db_engine()
    session = create_db_session(engine)

    query = """
            CREATE TABLE IF NOT EXISTS websocket (
                id VARCHAR(36) PRIMARY KEY,
                connection_id TEXT NOT NULL,
                file_name TEXT,
                user_id TEXT
            );
        """

    session.execute(query)
    session.commit()

    pass


def downgrade():
    pass
