"""alter_margin_column_in_company_table

Revision ID: c36c65c78855
Revises: 143ff6eab726
Create Date: 2022-03-10 10:05:41.156645

"""

from utils.connection import create_db_engine, create_db_session

# revision identifiers, used by Alembic.
revision = "c36c65c78855"
down_revision = "143ff6eab726"
branch_labels = None
depends_on = None


def upgrade():
    engine = create_db_engine()
    session = create_db_session(engine)

    query = """
           ALTER TABLE company ALTER COLUMN margin_group DROP NOT NULL;
        """

    session.execute(query)
    session.commit()

    pass


def downgrade():
    pass
