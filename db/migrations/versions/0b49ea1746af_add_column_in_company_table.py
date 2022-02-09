"""add_column_in_company_table

Revision ID: 0b49ea1746af
Revises: 4f7b7144cffa
Create Date: 2022-02-09 12:34:37.924362

"""
from utils.connection import create_db_engine, create_db_session

# revision identifiers, used by Alembic.
revision = "0b49ea1746af"
down_revision = "4f7b7144cffa"
branch_labels = None
depends_on = None


def upgrade():
    engine = create_db_engine()
    session = create_db_session(engine)

    query = """
            ALTER TABLE company
            ADD COLUMN is_public BOOLEAN NOT NULL DEFAULT true;
        """

    session.execute(query)
    session.commit()

    pass


def downgrade():
    pass
