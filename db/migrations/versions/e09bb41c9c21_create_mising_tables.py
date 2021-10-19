"""create-mising-tables

Revision ID: e09bb41c9c21
Revises: 220f0c0497b4
Create Date: 2021-10-19 16:13:16.373855

"""
from utils.connection import create_db_engine, create_db_session


# revision identifiers, used by Alembic.
revision = "e09bb41c9c21"
down_revision = "220f0c0497b4"
branch_labels = None
depends_on = None


def upgrade():
    engine = create_db_engine()
    session = create_db_session(engine)

    query = """
            CREATE TABLE IF NOT EXISTS currency_metric (
                id serial PRIMARY KEY,
                currency_iso_code VARCHAR(3) NOT NULL,
                metric_id INTEGER REFERENCES metric (id)
            );
            CREATE TABLE IF NOT EXISTS custom_metric (
                id serial PRIMARY KEY,
                formula VARCHAR(50) NOT NULL,
                metric_id INTEGER REFERENCES metric (id)
            );
            CREATE TABLE IF NOT EXISTS financial_scenario (
                id serial PRIMARY KEY,
                name VARCHAR(40) NOT NULL,
                currency VARCHAR(3) NOT NULL,
                type VARCHAR(30) NOT NULL,
                period_id INTEGER REFERENCES time_period (id),
                company_id INTEGER REFERENCES company (id)
            );
            CREATE TABLE IF NOT EXISTS scenario_metric (
                id serial PRIMARY KEY,
                metric_id INTEGER REFERENCES metric (id),
                scenario_id INTEGER REFERENCES financial_scenario (id)
            );
            CREATE TABLE IF NOT EXISTS location (
                id serial PRIMARY KEY,
                name VARCHAR(40) NOT NULL,
                country VARCHAR(40) NOT NULL,
                city VARCHAR(40) NOT NULL,
                lat NUMERIC NOT NULL,
                long NUMERIC NOT NULL,
                company_id INTEGER REFERENCES company (id)
            );
            CREATE TABLE IF NOT EXISTS portfolio (
                id serial PRIMARY KEY,
                name VARCHAR(40) NOT NULL,
                tag VARCHAR(40) NOT NULL
            );
            CREATE TABLE IF NOT EXISTS portfolio_company (
                id serial PRIMARY KEY,
                portfolio_id INTEGER REFERENCES portfolio (id),
                company_id INTEGER REFERENCES company (id)
            );
        """

    session.execute(query)
    session.commit()

    pass


def downgrade():
    pass
