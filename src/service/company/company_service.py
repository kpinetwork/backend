class CompanyService:
    def __init__(self, session, query_builder, logger, response_sql) -> None:
        self.table_name = "company"
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.logger = logger

    def get_company(self, company_id: str) -> dict:
        try:
            if company_id and company_id.strip():
                query = (
                    self.query_builder.add_table_name(self.table_name)
                    .add_select_conditions(
                        [f"{self.table_name}.*", "company_location.city"]
                    )
                    .add_join_clause(
                        {
                            "company_location": {
                                "from": f"{self.table_name}.id",
                                "to": "company_location.company_id",
                            }
                        },
                        self.query_builder.JoinType.LEFT,
                    )
                    .add_sql_where_equal_condition(
                        {f"{self.table_name}.id": f"'{company_id}'"}
                    )
                    .build()
                    .get_query()
                )

                result = self.session.execute(query).fetchall()
                self.session.commit()

                return self.response_sql.process_query_result(result)
            return dict()

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_all_companies(self, offset=0, max_count=20) -> list:
        try:
            query = (
                self.query_builder.add_table_name(self.table_name)
                .add_select_conditions(
                    [f"{self.table_name}.*", "company_location.city"]
                )
                .add_join_clause(
                    {
                        "company_location": {
                            "from": f"{self.table_name}.id",
                            "to": "company_location.company_id",
                        }
                    },
                    self.query_builder.JoinType.LEFT,
                )
                .add_sql_offset_condition(offset)
                .add_sql_limit_condition(max_count)
                .build()
                .get_query()
            )
            results = self.session.execute(query).fetchall()
            self.session.commit()
            return self.response_sql.process_query_list_results(results)

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_revenue_sum_by_company(self) -> list:
        columns = [
            f"{self.table_name}.id",
            f"{self.table_name}.name",
            "metrics.revenue_sum",
        ]
        try:
            subquery = (
                self.query_builder.add_table_name("metric")
                .add_select_conditions(
                    ["SUM(metric.value) as revenue_sum", "metric.company_id"]
                )
                .add_sql_where_equal_condition({"metric.name": "'Revenue'"})
                .add_sql_group_by_condition(["metric.company_id"])
                .build()
                .get_query()
            )

            query = (
                self.query_builder.add_table_name(self.table_name)
                .add_select_conditions(columns)
                .add_join_clause(
                    {
                        f"( {subquery} ) metrics ": {
                            "from": "metrics.company_id",
                            "to": f"{self.table_name}.id",
                        }
                    }
                )
                .build()
                .get_query()
            )
            results = self.session.execute(query).fetchall()
            self.session.commit()

            return self.response_sql.process_query_list_results(results)
        except Exception as error:
            self.logger.info(error)
            raise error
