"""create_first_db_schema

Revision ID: 220f0c0497b4
Revises:
Create Date: 2021-09-28 08:20:33.797602

"""

from utils.connection import create_db_engine, create_db_session


# revision identifiers, used by Alembic.
revision = "220f0c0497b4"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    engine = create_db_engine()
    session = create_db_session(engine)

    query = """"
            CREATE TABLE IF NOT EXISTS company (
                id serial PRIMARY KEY,
                name VARCHAR(40) NOT NULL,
                from_date DATE NOT NULL,
                fiscal_year DATE NOT NULL,
                sector VARCHAR(30) NOT NULL,
                vertical VARCHAR(30),
                inves_profile_name VARCHAR(40)
            );

            CREATE TABLE IF NOT EXISTS time_period (
                id serial PRIMARY KEY,
                start_at DATE NOT NULL,
                end_at DATE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS metric (
                id serial PRIMARY KEY,
                name VARCHAR(40) NOT NULL,
                value NUMERIC NOT NULL,
                type VARCHAR(8) NOT NULL,
                data_type VARCHAR(15) NOT NULL,
                period_id INTEGER REFERENCES time_period (id),
                company_id INTEGER REFERENCES company (id)
            );
    """

    session.execute(query)
    session.commit()

    pass


def downgrade():
    pass
