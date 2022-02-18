class UniverseOverviewService:
    def __init__(
        self, session, query_builder, logger, response_sql, company_anonymization
    ) -> None:
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.company_anonymization = company_anonymization
        self.logger = logger
        self.metric_table = "metric"
        self.company_table = "company"
        self.scenario_table = "financial_scenario"
        self.scenario_metric_table = "scenario_metric"

    def add_company_filters(self, **kwargs) -> dict:
        filters = dict()
        for k, v in kwargs.items():
            values = [f"'{element}'" for element in v if element and element.strip()]
            filters[f"{self.company_table}.{k}"] = values
        return filters

    def get_metric_avg_by_scenario(
        self,
        scenario_type: str,
        metric: str,
        year: str,
        sectors: list,
        verticals: list,
        investor_profile: list,
        growth_profile: list,
        size: list,
        avg_alias: str,
    ) -> dict:
        try:
            where_condition = {
                f"{self.scenario_table}.name": f"'{scenario_type}-{year}'",
                f"{self.metric_table}.name": f"'{metric}'",
                f"{self.company_table}.is_public": True,
            }
            filters = self.add_company_filters(
                sector=sectors,
                vertical=verticals,
                inves_profile_name=investor_profile,
                margin_group=growth_profile,
                size_cohort=size,
            )
            where_condition = dict(where_condition, **filters)

            query = (
                self.query_builder.add_table_name(self.company_table)
                .add_select_conditions(
                    [f"AVG({self.metric_table}.value) as {avg_alias}"]
                )
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

    def get_companies_kpi_average(
        self,
        sector: list,
        vertical: list,
        investor_profile: list,
        growth_profile: list,
        size: list,
        year: str,
    ) -> list:
        try:
            kpi_averages = []
            metrics = [
                {"scenario": "Actual growth", "metric": "Revenue", "alias": "growth"},
                {
                    "scenario": "Actual margin",
                    "metric": "Ebitda",
                    "alias": "ebitda_margin",
                },
                {"scenario": "Actuals", "metric": "Rule of 40", "alias": "rule_of_40"},
            ]
            for metric in metrics:
                metric_average = self.get_metric_avg_by_scenario(
                    metric.get("scenario"),
                    metric.get("metric"),
                    year,
                    sector,
                    vertical,
                    investor_profile,
                    growth_profile,
                    size,
                    metric.get("alias"),
                )
                kpi_averages.append(metric_average)

            return self.response_sql.process_query_list_results(kpi_averages)
        except Exception as error:
            self.logger.info(error)
            raise error

    def get_companies_count_by_size(
        self,
        sectors: list,
        verticals: list,
        investor_profile: list,
        growth_profile: list,
        size: list,
    ) -> list:
        try:
            where_conditions = self.add_company_filters(
                sector=sectors,
                vertical=verticals,
                inves_profile_name=investor_profile,
                margin_group=growth_profile,
                size_cohort=size,
            )
            where_conditions.update({f"{self.company_table}.is_public": True})

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
        sectors: list,
        verticals: list,
        investor_profile: list,
        growth_profile: list,
        size: list,
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

                where_conditions = {
                    f"{self.scenario_table}.name": f"'{scenario_name}'",
                    f"{self.metric_table}.name": f"'{metric}'",
                    f"{self.company_table}.is_public": True,
                }

                filters = self.add_company_filters(
                    sector=sectors,
                    vertical=verticals,
                    inves_profile_name=investor_profile,
                    margin_group=growth_profile,
                    size_cohort=size,
                )
                where_conditions = dict(where_conditions, **filters)

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
                    .add_sql_where_equal_condition(where_conditions)
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
        sectors: list,
        verticals: list,
        investor_profile: list,
        growth_profile: list,
        size: list,
        year: str,
    ) -> list:
        try:
            scenarios_result = []

            for scenario in scenarios:
                scenario_result = self.get_metric_avg_by_size_cohort(
                    scenario.get("scenario"),
                    scenario.get("metric"),
                    sectors,
                    verticals,
                    investor_profile,
                    growth_profile,
                    size,
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
        self,
        sectors: list,
        verticals: list,
        investor_profile: list,
        growth_profile: list,
        size: list,
        year: str,
        is_actual: bool = True,
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
                scenarios,
                sectors,
                verticals,
                investor_profile,
                growth_profile,
                size,
                year,
            )
        except Exception as error:
            self.logger.info(error)
            raise error

    def get_revenue_and_ebitda_by_size_cohort(
        self,
        sectors: list,
        verticals: list,
        investor_profile: list,
        growth_profile: list,
        size: list,
        year: str,
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
                scenarios,
                sectors,
                verticals,
                investor_profile,
                growth_profile,
                size,
                year,
            )
        except Exception as error:
            self.logger.info(error)
            raise error

    def get_rule_of_40(
        self,
        sectors: list,
        verticals: list,
        investor_profile: list,
        growth_profile: list,
        size: list,
        year: str,
        access: bool,
    ) -> list:
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

            where_conditions = self.add_company_filters(
                sector=sectors,
                vertical=verticals,
                inves_profile_name=investor_profile,
                margin_group=growth_profile,
                size_cohort=size,
            )
            where_conditions.update({f"{self.company_table}.is_public": True})

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
                .add_sql_where_equal_condition(where_conditions)
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
            rule_of_40 = self.response_sql.process_query_list_results(results)
            if access:
                return rule_of_40
            else:
                return self.company_anonymization.anonymize_companies_list(
                    rule_of_40, "company_id"
                )
        except Exception as error:
            self.logger.info(error)
            raise error

    def get_universe_overview(
        self,
        sectors: list,
        verticals: list,
        investor_profile: list,
        growth_profile: list,
        size: list,
        year: str,
        access: bool,
    ) -> dict:
        try:
            kpi_average = self.get_companies_kpi_average(
                sectors, verticals, investor_profile, growth_profile, size, year
            )
            count_by_size = self.get_companies_count_by_size(
                sectors, verticals, investor_profile, growth_profile, size
            )
            growth_and_margin = self.get_growth_and_margin_by_size_cohort(
                sectors, verticals, investor_profile, growth_profile, size, year, True
            )
            expected_growth_and_margin = self.get_growth_and_margin_by_size_cohort(
                sectors, verticals, investor_profile, growth_profile, size, year, False
            )
            revenue_and_ebitda = self.get_revenue_and_ebitda_by_size_cohort(
                sectors, verticals, investor_profile, growth_profile, size, year
            )
            rule_of_40 = self.get_rule_of_40(
                sectors, verticals, investor_profile, growth_profile, size, year, access
            )

            return {
                "kpi_average": kpi_average,
                "count_by_size": count_by_size,
                "growth_and_margin": growth_and_margin,
                "expected_growth_and_margin": expected_growth_and_margin,
                "revenue_and_ebitda": revenue_and_ebitda,
                "rule_of_40": rule_of_40,
            }
        except Exception as error:
            self.logger.info(error)
            raise error
