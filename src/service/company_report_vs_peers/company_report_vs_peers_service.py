class CompanyReportvsPeersService:
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
        self.time_period_table = "time_period"

    def add_company_filters(self, **kwargs) -> dict:
        filters = dict()
        for k, v in kwargs.items():
            values = [f"'{element}'" for element in v if element and element.strip()]
            filters[f"{self.company_table}.{k}"] = values
        return filters

    def get_description(self, company_id: str, access) -> dict:
        try:
            if company_id and company_id.strip():
                query = (
                    self.query_builder.add_table_name(self.company_table)
                    .add_select_conditions(
                        [
                            f"{self.company_table}.id",
                            f"{self.company_table}.name",
                            f"{self.company_table}.sector",
                            f"{self.company_table}.vertical",
                            f"{self.company_table}.inves_profile_name",
                            f"{self.company_table}.size_cohort",
                            f"{self.company_table}.margin_group",
                        ]
                    )
                    .add_sql_where_equal_condition(
                        {
                            f"{self.company_table}.id": f"'{company_id}'",
                            f"{self.company_table}.is_public": True,
                        }
                    )
                    .build()
                    .get_query()
                )

                result = self.session.execute(query).fetchall()
                self.session.commit()
                company_description = self.response_sql.process_query_result(result)
                if access:
                    return company_description
                else:
                    return self.company_anonymization.anonymize_company_description(
                        company_description, "id"
                    )

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_metric_by_scenario(
        self,
        company_id: str,
        scenario_name: str,
        metric: str,
        value_alias: str,
    ) -> dict:
        try:
            where_condition = {
                f"{self.company_table}.id": f"'{company_id}'",
                f"{self.scenario_table}.name": f"'{scenario_name}'",
                f"{self.metric_table}.name": f"'{metric}'",
                f"{self.company_table}.is_public": True,
            }

            query = (
                self.query_builder.add_table_name(self.company_table)
                .add_select_conditions([f"{self.metric_table}.value as {value_alias}"])
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
                .add_join_clause(
                    {
                        f"{self.time_period_table}": {
                            "from": f"{self.time_period_table}.id",
                            "to": f"{self.metric_table}.period_id",
                        }
                    }
                )
                .add_sql_where_equal_condition(where_condition)
                .add_sql_order_by_condition(
                    ["time_period.start_at"], self.query_builder.Order.DESC
                )
                .add_sql_limit_condition(1)
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            self.session.commit()
            return self.response_sql.process_query_result(result)

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_company_financial_profile(
        self,
        company_id: str,
        year: str,
    ) -> dict:
        try:
            next_year = int(year) + 1
            financial_profile = dict()
            metrics = [
                {
                    "scenario": f"Actuals-{year}",
                    "metric": "Revenue",
                    "alias": "annual_revenue",
                },
                {
                    "scenario": f"Actuals-{year}",
                    "metric": "Ebitda",
                    "alias": "annual_ebitda",
                },
                {
                    "scenario": f"Actuals-{year}",
                    "metric": "Rule of 40",
                    "alias": "anual_rule_of_40",
                },
                {
                    "scenario": f"Budgeted growth-{next_year}",
                    "metric": "Revenue",
                    "alias": "current_revenue_growth",
                },
                {
                    "scenario": f"Budgeted growth-{next_year}",
                    "metric": "Ebitda",
                    "alias": "current_ebitda_margin",
                },
                {
                    "scenario": f"Budget-{next_year}",
                    "metric": "Rule of 40",
                    "alias": "current_rule_of_40",
                },
            ]
            for metric in metrics:
                metric_average = self.get_metric_by_scenario(
                    company_id,
                    metric.get("scenario"),
                    metric.get("metric"),
                    metric.get("alias"),
                )

                if metric_average:
                    financial_profile.update(metric_average)
            return self.response_sql.process_query_result([financial_profile])
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
                    THEN {metric_table}.value ELSE NULL END
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
            rule_of_40 = self.response_sql.process_rule_of_40_chart_results(results)
            if access:
                return rule_of_40
            else:
                return self.company_anonymization.anonymize_companies_list(
                    rule_of_40, "company_id"
                )

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_company_report_vs_peers(
        self,
        company_id: str,
        sectors: list,
        verticals: list,
        investor_profile: list,
        growth_profile: list,
        size: list,
        year: str,
        access: bool,
    ) -> dict:
        try:
            company_description = self.get_description(company_id, access)
            if not company_description:
                return dict()

            company_financial_profile = self.get_company_financial_profile(
                company_id, year
            )
            rule_of_40 = self.get_rule_of_40(
                sectors, verticals, investor_profile, growth_profile, size, year, access
            )

            return {
                "description": company_description,
                "financial_profile": company_financial_profile,
                "rule_of_40": rule_of_40,
            }
        except Exception as error:
            self.logger.info(error)
            raise error
