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
            ALTER TABLE metric
            DROP COLUMN period_id,
            DROP COLUMN company_id,
            ALTER COLUMN id TYPE VARCHAR(36),
            ALTER COLUMN id DROP DEFAULT;

            ALTER TABLE time_period
            ALTER COLUMN id TYPE VARCHAR(36),
            ALTER COLUMN id DROP DEFAULT;

            ALTER TABLE company
            ALTER COLUMN id TYPE VARCHAR(36),
            ALTER COLUMN name TYPE VARCHAR(180),
            ALTER COLUMN id DROP DEFAULT,
            ADD COLUMN margin_group VARCHAR(8) NOT NULL;

            ALTER TABLE metric
            ADD COLUMN period_id VARCHAR(36) REFERENCES time_period (id),
            ADD COLUMN company_id VARCHAR(36) REFERENCES company (id);

            CREATE TABLE IF NOT EXISTS currency_metric (
                id VARCHAR(36) PRIMARY KEY,
                currency_iso_code VARCHAR(3) NOT NULL,
                metric_id VARCHAR(36) REFERENCES metric (id)
            );
            CREATE TABLE IF NOT EXISTS custom_metric (
                id VARCHAR(36) PRIMARY KEY,
                formula TEXT NOT NULL,
                metric_id VARCHAR(36) REFERENCES metric (id)
            );
            CREATE TABLE IF NOT EXISTS financial_scenario (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(40) NOT NULL,
                currency VARCHAR(3) NOT NULL,
                type VARCHAR(30) NOT NULL,
                period_id VARCHAR(36) REFERENCES time_period (id),
                company_id VARCHAR(36) REFERENCES company (id)
            );
            CREATE TABLE IF NOT EXISTS scenario_metric (
                id VARCHAR(36) PRIMARY KEY,
                metric_id VARCHAR(36) REFERENCES metric (id),
                scenario_id VARCHAR(36) REFERENCES financial_scenario (id)
            );
            CREATE TABLE IF NOT EXISTS company_location (
                id VARCHAR(36) PRIMARY KEY,
                address VARCHAR(100),
                country VARCHAR(60) NOT NULL,
                city VARCHAR(80) NOT NULL,
                geo POINT,
                company_id VARCHAR(36) REFERENCES company (id)
            );
            CREATE TABLE IF NOT EXISTS cohort (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(40) NOT NULL,
                tag VARCHAR(40) NOT NULL
            );
            CREATE TABLE IF NOT EXISTS cohort_company (
                id VARCHAR(36) PRIMARY KEY,
                cohort_id VARCHAR(36) REFERENCES cohort (id),
                company_id VARCHAR(36) REFERENCES company (id)
            );
        """

    session.execute(query)
    session.commit()

    pass


def downgrade():
    pass
