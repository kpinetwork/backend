from db_connection import create_db_engine, create_db_session

table_name = "company"

engine = create_db_engine()
session = create_db_session(engine)

def get_company(company_id: str) -> dict:

    if company_id and company_id.strip():

        query = "SELECT * FROM {table_name} WHERE id='{id}';".format(
            table_name=table_name, id=company_id
        )

        result = session.execute(query)
        session.commit()

        company = next(result)
        return dict(company) if company else dict()
    return dict()
