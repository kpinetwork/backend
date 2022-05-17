"""create_investment_table

Revision ID: 051ca978f7ec
Revises: 048dd8a08bdf
Create Date: 2022-05-16 10:34:12.538098

"""
from utils.connection import create_db_engine, create_db_session


# revision identifiers, used by Alembic.
revision = "051ca978f7ec"
down_revision = "048dd8a08bdf"
branch_labels = None
depends_on = None


def upgrade():
    engine = create_db_engine()
    session = create_db_session(engine)

    query = """
            CREATE TABLE IF NOT EXISTS investment (
                id VARCHAR(36) PRIMARY KEY,
                company_id VARCHAR(36) REFERENCES company (id),
                investment_date DATE,
                divestment_date DATE,
                round INTEGER,
                structure TEXT,
                ownership TEXT,
                investor_type TEXT
            );

            CREATE TABLE IF NOT EXISTS investor (
                id VARCHAR(36) PRIMARY KEY,
                investment_id VARCHAR(36) REFERENCES investment (id),
                firm_name TEXT
            );
        """

    session.execute(query)
    session.commit()

    pass


def downgrade():
    pass
