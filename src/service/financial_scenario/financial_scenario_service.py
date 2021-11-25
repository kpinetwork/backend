class FinancialScenarioService:
    def __init__(self, session, query_builder, logger, response_sql) -> None:
        self.table_name = "financial_scenario"
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.logger = logger
        pass

    def get_scenarios(self, offset=0, max_count=40) -> list:
        columns = [
            f"{self.table_name}.id",
            f"{self.table_name}.name",
            "company.id as company_id",
            "company.name as company_name",
            "metric.id as metric_id",
            "metric.name as metric_name",
            "metric.value as metric_value",
            "metric.type as metric_type",
            "metric.data_type as metric_data_type",
        ]
        try:
            query = (
                self.query_builder.add_table_name(self.table_name)
                .add_select_conditions(columns)
                .add_join_clause(
                    {
                        "company": {
                            "from": "company.id",
                            "to": f"{self.table_name}.company_id",
                        }
                    }
                )
                .add_join_clause(
                    {
                        "scenario_metric": {
                            "from": "scenario_metric.scenario_id",
                            "to": f"{self.table_name}.id",
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
                .add_sql_order_by_condition("company.id", self.query_builder.Order.ASC)
                .add_sql_offset_condition(offset)
                .add_sql_limit_condition(max_count)
                .build()
                .get_query()
            )

            results = self.session.execute(query).fetchall()
            self.session.commit()

            return self.response_sql.process_scenarios_list_results(results)

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_company_scenarios(
        self, company_id: str, scenario_type: str, offset=0, max_count=20
    ) -> list:
        columns = [
            f"{self.table_name}.id",
            f"{self.table_name}.name",
            f"{self.table_name}.currency",
            f"{self.table_name}.type",
            f"{self.table_name}.period_id",
            "time_period.start_at",
            "time_period.end_at",
            "metric.id as metric_id",
            "metric.name as metric_name",
            "metric.value as metric_value",
            "metric.type as metric_type",
            "metric.data_type as metric_data_type",
        ]

        try:
            if company_id and company_id.strip():
                where_conditions = {f"{self.table_name}.company_id": f"'{company_id}'"}

                if scenario_type and scenario_type.strip():
                    where_conditions[f"{self.table_name}.type"] = f"'{scenario_type}'"

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
                                "from": "scenario_metric.scenario_id",
                                "to": f"{self.table_name}.id",
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
                    .add_sql_where_equal_condition(where_conditions)
                    .add_sql_offset_condition(offset)
                    .add_sql_limit_condition(max_count)
                    .build()
                    .get_query()
                )

                results = self.session.execute(query).fetchall()
                self.session.commit()

                return self.response_sql.process_query_list_results(results)
            return []
        except Exception as error:
            self.logger.info(error)
            raise error

    def list_scenarios(self, company_id: str, offset=0, max_count=20) -> list:
        try:
            where_conditions = dict()
            if company_id and company_id.strip():
                where_conditions[f"{self.table_name}.company_id"] = f"'{company_id}'"

            query = (
                self.query_builder.add_select_conditions(["id", "name"])
                .add_table_name(self.table_name)
                .add_sql_where_equal_condition(where_conditions)
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
