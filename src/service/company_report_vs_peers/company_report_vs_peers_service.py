from typing import Union


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

    def is_valid_number(self, number: float):
        return number is not None and not isinstance(number, str)

    def convert_to_int_if_valid(self, value: Union[float, str]) -> Union[float, str]:
        if isinstance(value, (int, float)):
            return int(value)
        return value

    def calculate_growth_rate(
        self, metric_value_recent_year: float, metric_value_prior_year: float
    ) -> Union[float, str]:
        try:
            if self.is_valid_number(metric_value_recent_year) and self.is_valid_number(
                metric_value_prior_year
            ):
                return round(
                    ((metric_value_recent_year / metric_value_prior_year) - 1) * 100, 2
                )
            return "NA"
        except Exception as error:
            self.logger.info(error)
            return "NA"

    def calculate_ebitda_margin(
        self, ebitda: float, revenue: float
    ) -> Union[float, str]:
        try:
            if self.is_valid_number(ebitda) and revenue:
                return (ebitda / revenue) * 100
            return "NA"
        except Exception as error:
            self.logger.info(error)
            return "NA"

    def calculate_rule_of_40(
        self,
        revenue_recent_year: float,
        revenue_prior_year: float,
        ebitda_recent_year: float,
    ) -> Union[float, str]:
        revenue_growth = self.calculate_growth_rate(
            revenue_recent_year, revenue_prior_year
        )
        ebitda_margin = self.calculate_ebitda_margin(
            ebitda_recent_year, revenue_recent_year
        )
        if self.is_valid_number(revenue_growth) and self.is_valid_number(ebitda_margin):
            return round(revenue_growth + ebitda_margin, 2)
        return "NA"

    def get_base_metrics(self, company_id: str, year: str) -> dict():
        try:
            prior_year = int(year) - 1
            next_year = int(year) + 1
            base_metrics = dict()
            metrics = [
                {
                    "scenario": f"Actuals-{year}",
                    "metric": "Revenue",
                    "alias": "actuals_revenue_current_year",
                },
                {
                    "scenario": f"Actuals-{year}",
                    "metric": "Ebitda",
                    "alias": "actuals_ebitda_current_year",
                },
                {
                    "scenario": f"Actuals-{prior_year}",
                    "metric": "Revenue",
                    "alias": "actuals_revenue_prior_year",
                },
                {
                    "scenario": f"Budget-{year}",
                    "metric": "Revenue",
                    "alias": "budget_revenue_current_year",
                },
                {
                    "scenario": f"Budget-{year}",
                    "metric": "Ebitda",
                    "alias": "budget_ebitda_current_year",
                },
                {
                    "scenario": f"Budget-{next_year}",
                    "metric": "Revenue",
                    "alias": "budget_revenue_next_year",
                },
                {
                    "scenario": f"Budget-{next_year}",
                    "metric": "Ebitda",
                    "alias": "budget_ebitda_next_year",
                },
            ]
            for metric in metrics:
                base_metric = self.get_metric_by_scenario(
                    company_id,
                    metric.get("scenario"),
                    metric.get("metric"),
                    metric.get("alias"),
                )
                if base_metric:
                    base_metrics.update(base_metric)
            return base_metrics

        except Exception as error:
            self.logger.info(error)
            raise error

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
            financial_profile = dict()
            base_metrics = self.get_base_metrics(company_id, year)
            annual_rule_of_40 = self.convert_to_int_if_valid(
                self.calculate_rule_of_40(
                    base_metrics.get("actuals_revenue_current_year", ""),
                    base_metrics.get("actuals_revenue_prior_year"),
                    base_metrics.get("actuals_ebitda_current_year", ""),
                )
            )
            forward_budgeted_revenue_growth = self.convert_to_int_if_valid(
                self.calculate_growth_rate(
                    base_metrics.get("budget_revenue_next_year", ""),
                    base_metrics.get("budget_revenue_current_year", ""),
                )
            )
            forward_budgeted_ebitda_growth = self.convert_to_int_if_valid(
                self.calculate_growth_rate(
                    base_metrics.get("budget_ebitda_next_year", ""),
                    base_metrics.get("budget_ebitda_current_year", ""),
                )
            )
            forward_budgeted_rule_of_40 = self.convert_to_int_if_valid(
                self.calculate_rule_of_40(
                    base_metrics.get("budget_revenue_next_year", ""),
                    base_metrics.get("budget_revenue_current_year"),
                    base_metrics.get("budget_ebitda_next_year", ""),
                )
            )

            financial_profile = {
                "annual_revenue": self.convert_to_int_if_valid(
                    base_metrics.get("actuals_revenue_current_year", "NA")
                ),
                "annual_ebitda": self.convert_to_int_if_valid(
                    base_metrics.get("actuals_ebitda_current_year", "NA")
                ),
                "anual_rule_of_40": annual_rule_of_40,
                "current_revenue_growth": forward_budgeted_revenue_growth,
                "current_ebitda_margin": forward_budgeted_ebitda_growth,
                "current_rule_of_40": forward_budgeted_rule_of_40,
            }
            return financial_profile

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
