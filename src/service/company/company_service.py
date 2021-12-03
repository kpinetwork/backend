class CompanyService:
    def __init__(self, session, query_builder, logger, response_sql) -> None:
        self.table_name = "company"
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.logger = logger
        pass

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

    def get_companies_kpi_average(
        self, scenario_type: str, metric: str, year: str, sector: str, vertical: str
    ) -> dict:
        try:
            where_condition = {
                "financial_scenario.name": f"'{scenario_type}-{year}'",
                "metric.name": f"'{metric}'",
            }

            if sector and sector.strip():
                where_condition[f"{self.table_name}.sector"] = f"'{sector}'"

            if vertical and vertical.strip():
                where_condition[f"{self.table_name}.vertical"] = f"{vertical}"

            query = (
                self.query_builder.add_table_name(self.table_name)
                .add_select_conditions(["AVG(metric.value) as average"])
                .add_join_clause(
                    {
                        "financial_scenario": {
                            "from": "financial_scenario.company_id",
                            "to": f"{self.table_name}.id",
                        }
                    }
                )
                .add_join_clause(
                    {
                        "scenario_metric": {
                            "from": "scenario_metric.scenario_id",
                            "to": "financial_scenario.id",
                        }
                    }
                )
                .add_join_clause(
                    {
                        "metric": {
                            "from": "scenario_metric.metric_id",
                            "to": "metric.id",
                        }
                    }
                )
                .add_sql_where_equal_condition(where_condition)
                .build()
                .get_query()
            )

            result = self.session.execute(query).fetchall()
            self.session.commit()
            return self.response_sql.process_query_result(result)

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_companies_count_by_size(self, sector: str, vertical: str) -> list:
        try:
            where_conditions = dict()
            if sector and sector.strip():
                where_conditions[f"{self.table_name}.sector"] = f"'{sector}'"
            if vertical and vertical.strip():
                where_conditions[f"{self.table_name}.vertical"] = f"'{vertical}'"
            query = (
                self.query_builder.add_table_name(self.table_name)
                .add_select_conditions(
                    [f"{self.table_name}.size_cohort", f"COUNT({self.table_name}.id)"]
                )
                .add_sql_where_equal_condition(where_conditions)
                .add_sql_group_by_condition([f"{self.table_name}.size_cohort"])
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
