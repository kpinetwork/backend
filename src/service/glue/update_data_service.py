class UpdateDataService:
    def __init__(self, session, query_builder, logger, response_sql) -> None:
        self.company_table_name = "company"
        self.metric_table_name = "metric"
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.logger = logger

    def update_data(self, companies: list, metrics: list) -> dict:
        try:
            queries = []

            if companies:
                queries.append(
                    self.get_update_queries(self.company_table_name, companies)
                )
            if metrics:
                queries.append(self.get_update_queries(self.metric_table_name, metrics))

            query = self.get_queries_joined(queries)

            self.session.execute(query)
            self.session.commit()

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_update_queries(
        self,
        table: str,
        rows_data: list,
    ) -> str:
        queries = []
        for row in rows_data:
            primary_key = row.pop("id")
            conditions = self.__get_valid_conditions(row)

            query = (
                self.query_builder.add_table_name(table)
                .add_set_conditions(conditions)
                .add_sql_where_equal_condition({f"{table}.id": f"'{primary_key}'"})
                .build_update()
                .get_query()
            )
            queries.append(query)
        return self.get_queries_joined(queries)

    def get_queries_joined(self, queries: list) -> str:
        return ";".join(queries)

    def __get_valid_conditions(self, conditions: dict) -> dict:
        return {
            key: (f"'{value}'" if isinstance(value, str) else value)
            for key, value in conditions.items()
        }
