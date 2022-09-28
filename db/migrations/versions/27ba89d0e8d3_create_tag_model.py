"""create_tag_model

Revision ID: 27ba89d0e8d3
Revises: 063e82762a30
Create Date: 2022-09-28 08:05:29.133464

"""
from utils.connection import create_db_engine, create_db_session

# revision identifiers, used by Alembic.
revision = "27ba89d0e8d3"
down_revision = "063e82762a30"
branch_labels = None
depends_on = None


def upgrade():
    engine = create_db_engine()
    session = create_db_session(engine)
    query = """
        CREATE TABLE IF NOT EXISTS tag (
            id VARCHAR(36) PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS company_tag (
            id VARCHAR(36) PRIMARY KEY,
            tag_id VARCHAR(36) REFERENCES tag (id),
            company_id VARCHAR(36) REFERENCES company (id)
        );
    """
    try:
        session.execute(query)
        session.commit()
    except Exception:
        session.rollback()


def downgrade():
    pass
