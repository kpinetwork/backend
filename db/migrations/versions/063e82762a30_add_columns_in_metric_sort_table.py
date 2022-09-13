"""add_columns_in_metric_sort_table

Revision ID: 063e82762a30
Revises: 82d43584a2b7
Create Date: 2022-09-12 15:38:07.874986

"""
from utils.connection import create_db_engine, create_db_session


# revision identifiers, used by Alembic.
revision = "063e82762a30"
down_revision = "82d43584a2b7"
branch_labels = None
depends_on = None


def upgrade():
    engine = create_db_engine()
    session = create_db_session(engine)

    query = """
            ALTER TABLE metric_sort
            ADD COLUMN group_name TEXT,
            ADD COLUMN group_sort_value NUMERIC;
        """

    session.execute(query)
    session.commit()


def downgrade():
    pass
