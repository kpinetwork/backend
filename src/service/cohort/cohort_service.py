class CohortService:
    def __init__(self, session, query_builder, logger, response_sql):
        self.session = session
        self.table_name = "cohort"
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.logger = logger
        pass

    def get_cohort_scenarios(
        self, cohort_id: str, scenario_type: str, year: str, offset=0, max_count=20
    ) -> list:
        try:
            if cohort_id and cohort_id.strip():
                columns = [
                    "financial_scenario.name as scenario_name",
                    "financial_scenario.currency as scenario_currency",
                    "financial_scenario.type as scenario_type",
                    "company.name as company_name",
                    "metric.name as metric_name",
                    "metric.value as metric_value",
                    "metric.type as metric_type",
                    "metric.data_type as metric_data_type",
                    "metric.name as metric_name",
                ]
                scenario_name = f"{scenario_type}-{year}"

                query = (
                    self.query_builder.add_table_name(f"{self.table_name}_company")
                    .add_select_conditions(columns)
                    .add_join_clause(
                        {
                            "financial_scenario": {
                                "from": "financial_scenario.company_id",
                                "to": f"{self.table_name}_company.company_id",
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
                            "company": {
                                "from": "company.id",
                                "to": f"{self.table_name}_company.company_id",
                            }
                        }
                    )
                    .add_join_clause(
                        {
                            "metric": {
                                "from": "metric.id",
                                "to": "scenario_metric.metric_id",
                            }
                        }
                    )
                    .add_sql_where_equal_condition(
                        {
                            "cohort_id": f"'{cohort_id}'",
                            "financial_scenario.type": f"'{scenario_type}'",
                            "financial_scenario.name": f"'{scenario_name}'",
                        }
                    )
                    .add_sql_offset_condition(offset)
                    .add_sql_limit_condition(max_count)
                    .build()
                    .get_query()
                )
                result = self.session.execute(query).fetchall()
                self.session.commit()
                return self.response_sql.process_query_list_results(result)
            return []

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_cohort_information_by_id(self, cohort_id: str) -> dict:
        try:
            if cohort_id and cohort_id.strip():
                columns = [
                    "COUNT(company.id) as total_companies",
                    "array_agg(DISTINCT(company.vertical)) as companies_vertical",
                    "array_agg(DISTINCT(company.sector)) as companies_sector",
                    "array_agg(DISTINCT(company.margin_group)) as companies_margin_group",
                    "cohort.id  as cohort_id",
                    "cohort.name as cohort_name",
                    "cohort.tag as cohort_tag",
                ]

                query = (
                    self.query_builder.add_table_name(f"{self.table_name}")
                    .add_select_conditions(columns)
                    .add_join_clause(
                        {
                            f"{self.table_name}_company": {
                                "from": f"{self.table_name}_company.cohort_id",
                                "to": f"{self.table_name}.id",
                            }
                        }
                    )
                    .add_join_clause(
                        {
                            "company": {
                                "from": "company.id",
                                "to": f"{self.table_name}_company.company_id",
                            }
                        }
                    )
                    .add_sql_where_equal_condition(
                        {f"{self.table_name}_company.cohort_id": f"'{cohort_id}'"}
                    )
                    .add_sql_group_by_condition(["cohort.id"])
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

    def get_cohorts(self, offset=0, max_count=20) -> list:
        try:
            columns = [
                "COUNT(company.id) as total_companies",
                "array_agg(DISTINCT(company.vertical)) as companies_vertical",
                "array_agg(DISTINCT(company.sector)) as companies_sector",
                "array_agg(DISTINCT(company.margin_group)) as companies_margin_group",
                "cohort.id  as cohort_id",
                "cohort.name as cohort_name",
                "cohort.tag as cohort_tag",
            ]

            query = (
                self.query_builder.add_table_name(f"{self.table_name}")
                .add_select_conditions(columns)
                .add_join_clause(
                    {
                        f"{self.table_name}_company": {
                            "from": f"{self.table_name}_company.cohort_id",
                            "to": f"{self.table_name}.id",
                        }
                    }
                )
                .add_join_clause(
                    {
                        "company": {
                            "from": "company.id",
                            "to": f"{self.table_name}_company.company_id",
                        }
                    }
                )
                .add_sql_group_by_condition(["cohort.id"])
                .add_sql_offset_condition(offset)
                .add_sql_limit_condition(max_count)
                .build()
                .get_query()
            )

            result = self.session.execute(query).fetchall()
            self.session.commit()
            return self.response_sql.process_query_list_results(result)

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_revenue_sum_by_cohort(self) -> list:
        try:
            columns = [
                "cohort_company.cohort_id",
                f"{self.table_name}.name",
                "SUM(metric.value) as revenue_sum ",
            ]
            print("her")
            query = (
                self.query_builder.add_table_name("metric")
                .add_select_conditions(columns)
                .add_join_clause(
                    {
                        "cohort_company": {
                            "from": "cohort_company.company_id",
                            "to": "metric.company_id",
                        }
                    }
                )
                .add_join_clause(
                    {
                        f"{self.table_name}": {
                            "from": f"{self.table_name}.id",
                            "to": "cohort_company.cohort_id",
                        }
                    }
                )
                .add_sql_where_equal_condition({"metric.name": "'Revenue'"})
                .add_sql_group_by_condition(
                    ["cohort_company.cohort_id", f"{self.table_name}.name"]
                )
                .build()
                .get_query()
            )

            result = self.session.execute(query).fetchall()
            self.session.commit()
            return self.response_sql.process_query_list_results(result)

        except Exception as error:
            self.logger.info(error)
            raise error
