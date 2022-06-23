class DeleteScenariosService:
    def __init__(self, session, query_builder, logger, response_sql) -> None:
        self.session = session
        self.query_builder = query_builder
        self.logger = logger
        self.response_sql = response_sql

    def delete_scenarios(
        self, company_id: str, scenarios: list, from_details: bool
    ) -> int:
        scenarios_deleted = 0
        if not from_details:
            for scenario in scenarios:
                scenario_is_deleted = self.delete_scenario_from_edit_scenarios(
                    scenario.get("name"),
                    scenario.get("year"),
                    company_id,
                    scenario.get("metric"),
                    scenario.get("value"),
                )
                if scenario_is_deleted:
                    scenarios_deleted += 1
        else:
            for scenario in scenarios:
                scenario_is_deleted = self.delete_scenario(
                    scenario.get("scenario_id"), scenario.get("metric_id")
                )
                if scenario_is_deleted:
                    scenarios_deleted += 1

        return scenarios_deleted

    def delete_query_metric(self, scenario_id: str, metric_id: str) -> str:
        query = """
        DELETE FROM currency_metric WHERE metric_id = '{metric_id}';
        DELETE FROM scenario_metric WHERE scenario_id = '{scenario_id}'
        AND metric_id = '{metric_id}';
        DELETE FROM metric WHERE id = '{metric_id}';
        """.format(
            scenario_id=scenario_id, metric_id=metric_id
        )
        return query

    def delete_metric(self, scenario_id: str, metric_id: str) -> bool:
        try:
            query_to_delete_metric = self.delete_query_metric(scenario_id, metric_id)
            query = """
            BEGIN;
            {query}
            COMMIT;
            """.format(
                query=query_to_delete_metric
            )
            self.session.execute(query)
            self.session.commit()
            return True
        except Exception as error:
            self.logger.info(error)
            return False

    def delete_scenario(self, scenario_id: str, metric_id: str) -> bool:
        period_id = self.get_time_period_of_scenario(scenario_id)
        metric_is_deleted = self.delete_metric(scenario_id, metric_id)
        scenario_has_metric = self.scenario_is_in_scenario_metric(scenario_id)

        if (not metric_is_deleted) or (metric_is_deleted and scenario_has_metric):
            return metric_is_deleted

        try:
            query_to_delete_scenario = """
            DELETE FROM financial_scenario WHERE id ='{scenario_id}';
            DELETE FROM time_period WHERE id = '{period_id}';
            """.format(
                scenario_id=scenario_id, period_id=period_id
            )
            query = """
            BEGIN;
            {query}
            COMMIT;
            """.format(
                query=query_to_delete_scenario
            )
            self.session.execute(query)
            self.session.commit()
            return True
        except Exception as error:
            self.logger.info(error)
            return False

    def delete_scenario_from_edit_scenarios(
        self, name, year, company_id, metric_name, metric_value
    ) -> bool:
        scenario_id = self.get_scenario_id(name, year, company_id)
        period_id = self.get_time_period_of_scenario(scenario_id)
        metric_id = self.get_metric_id(metric_name, company_id, metric_value, period_id)
        scenario_deleted = self.delete_scenario(scenario_id, metric_id)
        return scenario_deleted

    def get_time_period_of_scenario(self, scenario_id: str) -> str:
        try:
            query = (
                self.query_builder.add_table_name("financial_scenario")
                .add_select_conditions(["period_id"])
                .add_sql_where_equal_condition({"id": "'{}'".format(scenario_id)})
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            return self.response_sql.process_query_result(result).get("period_id")

        except Exception as error:
            self.logger.info(error)
            return None

    def get_metric_id(
        self, metric_name: str, company_id: str, metric_value: float, period_id: str
    ) -> str:
        try:
            query = (
                self.query_builder.add_table_name("metric")
                .add_select_conditions(["id"])
                .add_sql_where_equal_condition(
                    {
                        "name": "'{}'".format(metric_name),
                        "company_id": "'{}'".format(company_id),
                        "value": "'{}'".format(metric_value),
                        "period_id": "'{}'".format(period_id),
                    }
                )
                .build()
                .get_query()
            )

            result = self.session.execute(query).fetchall()
            return self.response_sql.process_query_result(result).get("id")

        except Exception as error:
            self.logger.info(error)
            return None

    def get_scenario_id(self, name: str, year: int, company_id: str) -> str:
        try:
            scenario_name = "{}-{}".format(name, year)
            query = (
                self.query_builder.add_table_name("financial_scenario")
                .add_select_conditions(["id"])
                .add_sql_where_equal_condition(
                    {
                        "name ": "'{}'".format(scenario_name),
                        "company_id": "'{}'".format(company_id),
                    }
                )
                .build()
                .get_query()
            )

            result = self.session.execute(query).fetchall()
            return self.response_sql.process_query_result(result).get("id")

        except Exception as error:
            self.logger.info(error)
            return None

    def scenario_is_in_scenario_metric(self, scenario_id: str) -> bool:
        try:
            query = (
                self.query_builder.add_table_name("scenario_metric")
                .add_select_conditions(["id"])
                .add_sql_where_equal_condition(
                    {"scenario_id": "'{}'".format(scenario_id)}
                )
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            if not result:
                return False
            return True
        except Exception as error:
            self.logger.info(error)
            return False
