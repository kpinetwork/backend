"""remove_fields_from_company

Revision ID: 80253de57d77
Revises: d452f28623f6
Create Date: 2022-04-12 08:39:06.557391

"""

from utils.connection import create_db_engine, create_db_session


# revision identifiers, used by Alembic.
revision = "80253de57d77"
down_revision = "d452f28623f6"
branch_labels = None
depends_on = None


def upgrade():
    engine = create_db_engine()
    session = create_db_session(engine)

    query = """
            ALTER TABLE company
            DROP COLUMN IF EXISTS from_date,
            DROP COLUMN IF EXISTS fiscal_year,
            DROP COLUMN IF EXISTS margin_group,
            DROP COLUMN IF EXISTS size_cohort;
        """

    session.execute(query)
    session.commit()

    pass


def downgrade():
    pass
