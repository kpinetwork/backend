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
                print(scenario)
                scenario_is_deleted = self.delete_scenario(
                    scenario["name"],
                    scenario["year"],
                    company_id,
                    scenario["metric"],
                    scenario["value"],
                )
                if scenario_is_deleted:
                    scenarios_deleted += 1
        else:
            for scenario in scenarios:
                scenario_is_deleted = self.delete_scenario_from_details(
                    scenario["scenario_id"], scenario["metric_id"]
                )
                if scenario_is_deleted:
                    scenarios_deleted += 1

        return scenarios_deleted

    def delete_currency(self, metric_id: str) -> bool:
        try:
            query = """
            DELETE FROM {table_name} WHERE metric_id = '{metric_id}'
            """.format(
                table_name="currency_metric", metric_id=metric_id
            )

            self.session.execute(query)
            self.session.commit()
            return True
        except Exception as error:
            self.logger.info(error)
            return False

    def delete_scenario_metric(self, scenario_id: str, metric_id: str) -> bool:
        currency_is_deleted = self.delete_currency(metric_id)

        if currency_is_deleted:
            try:
                query = """
                    DELETE FROM {table_name}
                    WHERE scenario_id = '{scenario_id}'
                    AND metric_id = '{metric_id}'
                """.format(
                    table_name="scenario_metric",
                    scenario_id=scenario_id,
                    metric_id=metric_id,
                )

                self.session.execute(query)
                self.session.commit()
                return True
            except Exception as error:
                self.logger.info(error)
                return False
        else:
            return False

    def delete_metric(self, scenario_id: str, metric_id: str) -> bool:
        scenario_metric_is_deleted = self.delete_scenario_metric(scenario_id, metric_id)
        if scenario_metric_is_deleted:
            try:
                query = """
                DELETE FROM {table_name} WHERE id = '{metric_id}'
                """.format(
                    table_name="metric", metric_id=metric_id
                )

                self.session.execute(query)
                self.session.commit()
                return True
            except Exception as error:
                self.logger.info(error)
                return False
        else:
            return False

    def delete_scenario_from_details(self, scenario_id: str, metric_id) -> bool:
        metric_is_deleted = self.delete_metric(scenario_id, metric_id)
        if metric_is_deleted:
            is_scenario = self.scenario_is_in_scenario_metric(scenario_id)
            if not is_scenario:
                period_id = self.get_time_period_of_scenario(scenario_id)
                scenario_deleted = False
                try:
                    query = """
                    DELETE FROM {table_name} WHERE id = '{scenario_id}'
                    """.format(
                        table_name="financial_scenario", scenario_id=scenario_id
                    )

                    self.session.execute(query)
                    self.session.commit()
                    scenario_deleted = True
                except Exception as error:
                    self.logger.info(error)
                    scenario_deleted = False

                if scenario_deleted:
                    self.delete_time_period(period_id)
                    return True
            else:
                return True
        else:
            return False

    def delete_scenario(
        self, name, year, company_id, metric_name, metric_value
    ) -> bool:
        print(name, year, company_id, metric_name, metric_value)
        metric_id = self.get_metric_id(metric_name, company_id, metric_value)
        scenario_id = self.get_scenario_id(name, year, company_id)
        metric_is_deleted = self.delete_metric(scenario_id, metric_id)
        print(metric_id)
        print(scenario_id)
        if metric_is_deleted:
            is_scenario = self.scenario_is_in_scenario_metric(scenario_id)
            if not is_scenario:
                period_id = self.get_time_period_of_scenario(scenario_id)
                scenario_deleted = False
                try:
                    query = """
                    DELETE FROM {table_name} WHERE id = '{scenario_id}'
                    """.format(
                        table_name="financial_scenario", scenario_id=scenario_id
                    )

                    self.session.execute(query)
                    self.session.commit()
                    scenario_deleted = True
                except Exception as error:
                    self.logger.info(error)
                    scenario_deleted = False

                if scenario_deleted:
                    self.delete_time_period(period_id)
                    return True
            else:
                return True
        else:
            return False

    def get_time_period_of_scenario(self, scenario_id: str):
        try:
            query = """
            SELECT period_id FROM {table_name} WHERE id = '{scenario_id}'
            """.format(
                table_name="financial_scenario", scenario_id=scenario_id
            )

            result = self.session.execute(query)
            return result.first()[0]

        except Exception as error:
            self.logger.info(error)
            return None

    def delete_time_period(self, period_id: str):
        query = """
        DELETE FROM {table_name} WHERE id = '{period_id}'
        """.format(
            table_name="time_period", period_id=period_id
        )

        self.session.execute(query)
        self.session.commit()

    def get_metric_id(self, metric_name: str, company_id: str, metric_value: float):
        try:
            query = """
            SELECT id FROM {table_name}
            WHERE company_id = '{company_id}'
            AND name = '{metric_name}'
            AND value = '{metric_value}'
            """.format(
                table_name="metric",
                company_id=company_id,
                metric_name=metric_name,
                metric_value=metric_value,
            )
            result = self.session.execute(query)
            return result.first()[0]

        except Exception as error:
            self.logger.info(error)
            return None

    def get_scenario_id(self, name: str, year: int, company_id: str):
        try:
            scenario_name = "{}-{}".format(name, year)
            query = """
            SELECT id FROM {table_name}
            WHERE company_id = '{company_id}'
            AND name = '{scenario_name}'
            """.format(
                table_name="financial_scenario",
                company_id=company_id,
                scenario_name=scenario_name,
            )

            result = self.session.execute(query)
            return result.first()[0]

        except Exception as error:
            self.logger.info(error)
            return None

    def scenario_is_in_scenario_metric(self, scenario_id: str) -> bool:
        try:
            query = """
            SELECT * FROM {table_name} WHERE scenario_id = '{scenario_id}'
            """.format(
                table_name="scenario_metric", scenario_id=scenario_id
            )

            result = self.session.execute(query).fetchall()
            if not result:
                return False
            else:
                return True
        except Exception as error:
            self.logger.info(error)
            return False
