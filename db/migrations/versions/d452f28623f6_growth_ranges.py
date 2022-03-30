"""growth_ranges

Revision ID: d452f28623f6
Revises: c36c65c78855
Create Date: 2022-03-23 15:30:59.231702

"""
from utils.connection import create_db_engine, create_db_session


# revision identifiers, used by Alembic.
revision = "d452f28623f6"
down_revision = "c36c65c78855"
branch_labels = None
depends_on = None


def upgrade():
    engine = create_db_engine()
    session = create_db_session(engine)

    query = """
            ALTER TABLE value_range
            ADD COLUMN IF NOT EXISTS type TEXT NOT NULL DEFAULT 'size profile';
        """

    session.execute(query)
    session.commit()

    pass


def downgrade():
    pass
