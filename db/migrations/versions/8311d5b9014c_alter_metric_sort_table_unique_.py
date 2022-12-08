"""alter_metric_sort_table_unique_constraint

Revision ID: 8311d5b9014c
Revises: 27ba89d0e8d3
Create Date: 2022-12-07 16:16:39.053942

"""

from utils.connection import create_db_engine, create_db_session


# revision identifiers, used by Alembic.
revision = "8311d5b9014c"
down_revision = "27ba89d0e8d3"
branch_labels = None
depends_on = None


def upgrade():
    engine = create_db_engine()
    session = create_db_session(engine)

    query = """
           ALTER TABLE metric_sort DROP CONSTRAINT metric_sort_sort_value_key;
        """

    session.execute(query)
    session.commit()

    pass


def downgrade():
    pass
