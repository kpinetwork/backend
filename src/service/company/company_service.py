class CompanyService:
    def __init__(self, session, query_sql, response_sql) -> None:
        self.table_name = "company"
        self.session = session
        self.query_sql = query_sql
        self.response_sql = response_sql
        pass

    def get_company(self, company_id: str) -> dict:
        try:
            if company_id and company_id.strip():
                query = self.query_sql.get_select_by_id_query(
                    self.table_name, company_id
                )

                result = self.session.execute(query)
                self.session.commit()
                records = result.fetchall()
                return self.response_sql.process_query_results(records)
            return dict()

        except Exception as error:
            raise error

    def get_all_companies(self, offset=0, max_count=20) -> list:
        try:
            query = self.query_sql.get_select_query(self.table_name, offset, max_count)

            results = self.session.execute(query)
            self.session.commit()

            companies = []
            [companies.append(dict(record)) for record in results]
            return companies

        except Exception as error:
            raise error
