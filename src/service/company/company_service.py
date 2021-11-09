class CompanyService:
    def __init__(self, session, query_builder, response_sql) -> None:
        self.table_name = "company"
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        pass

    def get_company(self, company_id: str) -> dict:
        try:
            if company_id and company_id.strip():
                query = (
                    self.query_builder.add_table_name(self.table_name)
                    .add_sql_where_equal_condition({"id": company_id})
                    .build()
                    .get_query()
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
            query = (
                self.query_builder.add_table_name(self.table_name)
                .add_sql_offset_condition(offset)
                .add_sql_limit_condition(max_count)
                .build()
                .get_query()
            )

            results = self.session.execute(query)
            self.session.commit()

            companies = []
            [companies.append(dict(record)) for record in results]
            return companies

        except Exception as error:
            raise error
