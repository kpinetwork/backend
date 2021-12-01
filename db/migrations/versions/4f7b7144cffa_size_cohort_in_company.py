"""size_cohort_in_company

Revision ID: 4f7b7144cffa
Revises: e09bb41c9c21
Create Date: 2021-12-01 16:02:13.796870

"""
from utils.connection import create_db_engine, create_db_session

# revision identifiers, used by Alembic.
revision = "4f7b7144cffa"
down_revision = "e09bb41c9c21"
branch_labels = None
depends_on = None


def upgrade():
    engine = create_db_engine()
    session = create_db_session(engine)

    query = """
            ALTER TABLE company
            ADD COLUMN size_cohort TEXT;
        """

    session.execute(query)
    session.commit()

    pass


def downgrade():
    pass
