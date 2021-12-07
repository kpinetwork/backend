class CompanyService:
    def __init__(self, session, query_builder, logger, response_sql) -> None:
        self.table_name = "company"
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.logger = logger

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
                avg_select = "AVG(metric.value)"

                if avg_alias and avg_alias.strip():
                    avg_select = f"{avg_select} as {avg_alias}"

                columns = [
                    f"{self.table_name}.size_cohort",
                    avg_select,
                ]

                where_condictions = {
                    "financial_scenario.name": f"'{scenario_name}'",
                    "metric.name": f"'{metric}'",
                }

                if sector and sector.strip():
                    where_condictions[f"{self.table_name}.sector"] = f"'{sector}'"

                if vertical and vertical.strip():
                    where_condictions[f"{self.table_name}.vertical"] = f"'{vertical}'"

                query = (
                    self.query_builder.add_table_name(self.table_name)
                    .add_select_conditions(columns)
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
                    .add_sql_where_equal_condition(where_condictions)
                    .add_sql_group_by_condition([f"{self.table_name}.size_cohort"])
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

    def get_growth_and_margin_by_size_cohort(
        self, sector: str, vertical: str, year: str
    ) -> dict:
        try:
            growth_revenue = self.get_metric_avg_by_size_cohort(
                "Actual growth", "Revenue", sector, vertical, year, "growth"
            )
            margin_ebitda = self.get_metric_avg_by_size_cohort(
                "Actual margin", "Ebitda", sector, vertical, year, "margin"
            )

            growth_revenue.extend(margin_ebitda)
            return self.response_sql.process_metrics_group_by_size_cohort_results(
                growth_revenue
            )
        except Exception as error:
            self.logger.info(error)
            raise error

    def get_expected_growth_and_margin_by_size_cohort(
        self, sector: str, vertical: str, year: str
    ) -> dict:
        try:
            growth_revenue = self.get_metric_avg_by_size_cohort(
                "Budgeted growth", "Revenue", sector, vertical, year, "growth"
            )
            margin_ebitda = self.get_metric_avg_by_size_cohort(
                "Budgeted margin", "Ebitda", sector, vertical, year, "margin"
            )

            growth_revenue.extend(margin_ebitda)
            return self.response_sql.process_metrics_group_by_size_cohort_results(
                growth_revenue
            )
        except Exception as error:
            self.logger.info(error)
            raise error

    def get_revenue_and_ebitda_by_size_cohort(
        self, sector: str, vertical: str, year: str
    ) -> dict:
        try:
            revenue = self.get_metric_avg_by_size_cohort(
                "Actual vs budget", "Revenue", sector, vertical, year, "Revenue"
            )
            ebitda = self.get_metric_avg_by_size_cohort(
                "Actual vs budget", "Ebitda", sector, vertical, year, "Ebitda"
            )

            revenue.extend(ebitda)
            return self.response_sql.process_metrics_group_by_size_cohort_results(
                revenue
            )
        except Exception as error:
            self.logger.info(error)
            raise error

    def get_rule_of_40(self, sector: str, vertical: str, year: str) -> dict:
        def get_case_statement(scenario: str, metric: str, alias: str) -> str:
            return """
                SUM(
                    CASE WHEN financial_scenario.name = '{scenario}'
                    AND metric.name = '{metric}'
                    THEN metric.value ELSE 0 END
                ) AS {alias}
            """.format(
                scenario=scenario, metric=metric, alias=alias
            )

        try:
            scenario = "financial_scenario"
            columns = [
                f"{scenario}.{self.table_name}_id",
                f"{self.table_name}.name",
                get_case_statement(
                    f"Actual growth-{year}", "Revenue", "revenue_growth_rate"
                ),
                get_case_statement(f"Actual margin-{year}", "Ebitda", "ebitda_margin"),
                get_case_statement(f"Actuals-{year}", "Revenue", "revenue"),
            ]

            where_condictions = dict()

            if sector and sector.strip():
                where_condictions[f"{self.table_name}.sector"] = f"'{sector}'"

            if vertical and vertical.strip():
                where_condictions[f"{self.table_name}.vertical"] = f"'{vertical}'"

            query = (
                self.query_builder.add_table_name(self.table_name)
                .add_select_conditions(columns)
                .add_join_clause(
                    {
                        f"{scenario}": {
                            "from": f"{scenario}.{self.table_name}_id",
                            "to": f"{self.table_name}.id",
                        }
                    }
                )
                .add_join_clause(
                    {
                        "scenario_metric": {
                            "from": "scenario_metric.scenario_id",
                            "to": f"{scenario}.id",
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
                .add_sql_where_equal_condition(where_condictions)
                .add_sql_group_by_condition(
                    [f"{scenario}.{self.table_name}_id", f"{self.table_name}.name"]
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
