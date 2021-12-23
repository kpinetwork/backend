class MetricsService:
    def __init__(self, session, query_builder, logger, response_sql):
        self.session = session
        self.table_name = "metric"
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.logger = logger
        pass

    def get_metric_by_company_id(
        self, company_id: str, name: str, scenario_type: str
    ) -> list:
        try:
            if company_id and company_id.strip():
                columns = [
                    f"{self.table_name}.id",
                    f"{self.table_name}.name",
                    f"{self.table_name}.value",
                    f"{self.table_name}.type",
                    f"{self.table_name}.data_type",
                    f"{self.table_name}.period_id",
                    "time_period.start_at",
                    "time_period.end_at",
                    "financial_scenario.name as scenario",
                ]

                where_condition = {
                    f"{self.table_name}.company_id": f"'{company_id}'",
                }

                if name and name.strip():
                    where_condition[f"{self.table_name}.name"] = f"'{name}'"

                if scenario_type and scenario_type.strip():
                    where_condition["financial_scenario.type"] = f"'{scenario_type}'"

                query = (
                    self.query_builder.add_table_name(self.table_name)
                    .add_select_conditions(columns)
                    .add_join_clause(
                        {
                            "time_period": {
                                "from": "time_period.id",
                                "to": f"{self.table_name}.period_id",
                            }
                        }
                    )
                    .add_join_clause(
                        {
                            "scenario_metric": {
                                "from": "scenario_metric.metric_id",
                                "to": f"{self.table_name}.id",
                            }
                        }
                    )
                    .add_join_clause(
                        {
                            "financial_scenario": {
                                "from": "financial_scenario.id",
                                "to": "scenario_metric.scenario_id",
                            }
                        }
                    )
                    .add_sql_where_equal_condition(where_condition)
                    .add_sql_order_by_condition(
                        ["time_period.start_at"], self.query_builder.Order.DESC
                    )
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

    def get_metrics(self, offset=0, max_count=20) -> list:
        try:
            query = (
                self.query_builder.add_table_name(self.table_name)
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

    def get_average_metrics(self, name: str, company_id: str) -> int:
        try:
            if name and name.strip() and company_id and company_id.strip():
                query = (
                    self.query_builder.add_table_name(self.table_name)
                    .add_select_conditions(["AVG(value) as average"])
                    .add_sql_where_equal_condition(
                        {"name": f"'{name}'", "company_id": f"'{company_id}'"}
                    )
                    .build()
                    .get_query()
                )

                result = self.session.execute(query).fetchall()
                self.session.commit()

                return self.response_sql.process_query_average_result(result)
            return dict()

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_average_metrics_by_cohort(self, name: str, cohort_id: str) -> int:
        try:
            if name and name.strip() and cohort_id and cohort_id.strip():
                query = (
                    self.query_builder.add_table_name(self.table_name)
                    .add_select_conditions(["AVG(metric.value) as average"])
                    .add_join_clause(
                        {
                            "cohort_company": {
                                "from": "cohort_company.company_id",
                                "to": f"{self.table_name}.company_id",
                            }
                        }
                    )
                    .add_sql_where_equal_condition(
                        {
                            f"{self.table_name}.name": f"'{name}'",
                            "cohort_company.cohort_id": f"'{cohort_id}'",
                        }
                    )
                    .add_sql_group_by_condition(["cohort_company.cohort_id"])
                    .build()
                    .get_query()
                )

                result = self.session.execute(query).fetchall()
                self.session.commit()

                return self.response_sql.process_query_average_result(result)
            return dict()

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_metrics_by_cohort_id(
        self, cohort_id: str, name: str, scenario_type: str
    ) -> list:
        try:
            if cohort_id and cohort_id.strip():
                columns = [
                    f"AVG({self.table_name}.value) as value",
                    f"{self.table_name}.name",
                    f"array_agg(DISTINCT({self.table_name}.data_type)) as data_type",
                    f"array_agg(DISTINCT({self.table_name}.type)) as type",
                    "time_period.start_at",
                    "time_period.end_at",
                    "financial_scenario.type as scenario_type",
                ]

                where_condition = {
                    "cohort_company.cohort_id": f"'{cohort_id}'",
                }

                if name and name.strip():
                    where_condition[f"{self.table_name}.name"] = f"'{name}'"

                if scenario_type and scenario_type.strip():
                    where_condition["financial_scenario.type"] = f"'{scenario_type}'"

                query = (
                    self.query_builder.add_table_name(self.table_name)
                    .add_select_conditions(columns)
                    .add_join_clause(
                        {
                            "time_period": {
                                "from": "time_period.id",
                                "to": f"{self.table_name}.period_id",
                            },
                            "cohort_company": {
                                "from": "cohort_company.company_id",
                                "to": f"{self.table_name}.company_id",
                            },
                        }
                    )
                    .add_join_clause(
                        {
                            "scenario_metric": {
                                "from": "scenario_metric.metric_id",
                                "to": f"{self.table_name}.id",
                            }
                        }
                    )
                    .add_join_clause(
                        {
                            "financial_scenario": {
                                "from": "financial_scenario.id",
                                "to": "scenario_metric.scenario_id",
                            }
                        }
                    )
                    .add_sql_where_equal_condition(where_condition)
                    .add_sql_group_by_condition(
                        [
                            "time_period.start_at",
                            "time_period.end_at",
                            "financial_scenario.type",
                            f"{self.table_name}.name",
                        ]
                    )
                    .add_sql_order_by_condition(
                        ["time_period.start_at"], self.query_builder.Order.ASC
                    )
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
