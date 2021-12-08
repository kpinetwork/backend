class UniverseOverviewService:
    def __init__(self, session, query_builder, logger, response_sql) -> None:
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.logger = logger
        self.metric_table = "metric"
        self.company_table = "company"
        self.scenario_table = "financial_scenario"
        self.scenario_metric_table = "scenario_metric"

    def get_companies_count_by_size(self, sector: str, vertical: str) -> list:
        try:
            where_conditions = dict()
            if sector and sector.strip():
                where_conditions[f"{self.company_table}.sector"] = f"'{sector}'"

            if vertical and vertical.strip():
                where_conditions[f"{self.company_table}.vertical"] = f"'{vertical}'"

            query = (
                self.query_builder.add_table_name(self.company_table)
                .add_select_conditions(
                    [
                        f"{self.company_table}.size_cohort",
                        f"COUNT({self.company_table}.id)",
                    ]
                )
                .add_sql_where_equal_condition(where_conditions)
                .add_sql_group_by_condition([f"{self.company_table}.size_cohort"])
                .build()
                .get_query()
            )

            results = self.session.execute(query).fetchall()
            self.session.commit()
            return self.response_sql.process_query_list_results(results)

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_metric_avg_by_size_cohort(
        self,
        scenario: str,
        metric: str,
        sector: str,
        vertical: str,
        year: str,
        avg_alias: str,
    ) -> list:
        try:
            if scenario and scenario.strip() and metric and metric.strip():
                scenario_name = f"{scenario}-{year}"
                avg_select = f"AVG({self.metric_table}.value)"

                if avg_alias and avg_alias.strip():
                    avg_select = f"{avg_select} as {avg_alias}"

                columns = [
                    f"{self.company_table}.size_cohort",
                    avg_select,
                ]

                where_condictions = {
                    f"{self.scenario_table}.name": f"'{scenario_name}'",
                    f"{self.metric_table}.name": f"'{metric}'",
                }

                if sector and sector.strip():
                    where_condictions[f"{self.company_table}.sector"] = f"'{sector}'"

                if vertical and vertical.strip():
                    where_condictions[
                        f"{self.company_table}.vertical"
                    ] = f"'{vertical}'"

                query = (
                    self.query_builder.add_table_name(self.company_table)
                    .add_select_conditions(columns)
                    .add_join_clause(
                        {
                            f"{self.scenario_table}": {
                                "from": f"{self.scenario_table}.company_id",
                                "to": f"{self.company_table}.id",
                            }
                        }
                    )
                    .add_join_clause(
                        {
                            f"{self.scenario_metric_table}": {
                                "from": f"{self.scenario_metric_table}.scenario_id",
                                "to": f"{self.scenario_table}.id",
                            }
                        }
                    )
                    .add_join_clause(
                        {
                            f"{self.metric_table}": {
                                "from": f"{self.scenario_metric_table}.metric_id",
                                "to": f"{self.metric_table}.id",
                            }
                        }
                    )
                    .add_sql_where_equal_condition(where_condictions)
                    .add_sql_group_by_condition([f"{self.company_table}.size_cohort"])
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

    def get_scenarios_pair_by_size_cohort(
        self,
        scenarios: list,
        vertical: str,
        sector: str,
        year: str,
    ) -> list:
        try:
            scenarios_result = []

            for scenario in scenarios:
                scenario_result = self.get_metric_avg_by_size_cohort(
                    scenario.get("scenario"),
                    scenario.get("metric"),
                    sector,
                    vertical,
                    year,
                    scenario.get("avg_alias"),
                )
                scenarios_result.extend(scenario_result)

            return self.response_sql.process_metrics_group_by_size_cohort_results(
                scenarios_result
            )
        except Exception as error:
            self.logger.info(error)
            raise error

    def get_growth_and_margin_by_size_cohort(
        self, sector: str, vertical: str, year: str, is_actual: bool = True
    ) -> dict:
        try:
            scenario_type = "Actual" if is_actual else "Budgeted"
            scenarios = [
                {
                    "scenario": f"{scenario_type} growth",
                    "metric": "Revenue",
                    "avg_alias": "growth",
                },
                {
                    "scenario": f"{scenario_type} margin",
                    "metric": "Ebitda",
                    "avg_alias": "margin",
                },
            ]

            return self.get_scenarios_pair_by_size_cohort(
                scenarios, vertical, sector, year
            )
        except Exception as error:
            self.logger.info(error)
            raise error

    def get_revenue_and_ebitda_by_size_cohort(
        self, sector: str, vertical: str, year: str
    ) -> dict:
        try:
            scenario_type = "Actual vs budget"
            scenarios = [
                {
                    "scenario": f"{scenario_type}",
                    "metric": "Revenue",
                    "avg_alias": "revenue",
                },
                {
                    "scenario": f"{scenario_type}",
                    "metric": "Ebitda",
                    "avg_alias": "ebitda",
                },
            ]
            return self.get_scenarios_pair_by_size_cohort(
                scenarios, vertical, sector, year
            )
        except Exception as error:
            self.logger.info(error)
            raise error

    def get_rule_of_40(self, sector: str, vertical: str, year: str) -> dict:
        def get_case_statement(scenario: str, metric: str, alias: str) -> str:
            return """
                SUM(
                    CASE WHEN {scenario_table}.name = '{scenario}'
                    AND {metric_table}.name = '{metric}'
                    THEN {metric_table}.value ELSE 0 END
                ) AS {alias}
            """.format(
                scenario=scenario,
                metric=metric,
                alias=alias,
                scenario_table=self.scenario_table,
                metric_table=self.metric_table,
            )

        try:
            columns = [
                f"{self.scenario_table}.{self.company_table}_id",
                f"{self.company_table}.name",
                get_case_statement(
                    f"Actual growth-{year}", "Revenue", "revenue_growth_rate"
                ),
                get_case_statement(f"Actual margin-{year}", "Ebitda", "ebitda_margin"),
                get_case_statement(f"Actuals-{year}", "Revenue", "revenue"),
            ]

            where_condictions = dict()

            if sector and sector.strip():
                where_condictions[f"{self.company_table}.sector"] = f"'{sector}'"

            if vertical and vertical.strip():
                where_condictions[f"{self.company_table}.vertical"] = f"'{vertical}'"

            query = (
                self.query_builder.add_table_name(self.company_table)
                .add_select_conditions(columns)
                .add_join_clause(
                    {
                        f"{self.scenario_table}": {
                            "from": f"{self.scenario_table}.company_id",
                            "to": f"{self.company_table}.id",
                        }
                    }
                )
                .add_join_clause(
                    {
                        f"{self.scenario_metric_table}": {
                            "from": f"{self.scenario_metric_table}.scenario_id",
                            "to": f"{self.scenario_table}.id",
                        }
                    }
                )
                .add_join_clause(
                    {
                        f"{self.metric_table}": {
                            "from": f"{self.scenario_metric_table}.metric_id",
                            "to": f"{self.metric_table}.id",
                        }
                    }
                )
                .add_sql_where_equal_condition(where_condictions)
                .add_sql_group_by_condition(
                    [
                        f"{self.scenario_table}.{self.company_table}_id",
                        f"{self.company_table}.name",
                    ]
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

    def get_universe_overview(self, sector: str, vertical: str, year: str) -> dict:
        try:
            count_by_size = self.get_companies_count_by_size(sector, vertical)
            growth_and_margin = self.get_growth_and_margin_by_size_cohort(
                sector, vertical, year, True
            )
            expected_growth_and_margin = self.get_growth_and_margin_by_size_cohort(
                sector, vertical, year, False
            )
            revenue_and_ebitda = self.get_revenue_and_ebitda_by_size_cohort(
                sector, vertical, year
            )
            rule_of_40 = self.get_rule_of_40(sector, vertical, year)

            return {
                "count_by_size": count_by_size,
                "growth_and_margin": growth_and_margin,
                "expected_growth_and_margin": expected_growth_and_margin,
                "revenue_and_ebitda": revenue_and_ebitda,
                "rule_of_40": rule_of_40,
            }
        except Exception as error:
            self.logger.info(error)
            raise error
