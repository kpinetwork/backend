class ComparisonvsPeersService:
    def __init__(self, session, query_builder, logger, response_sql) -> None:
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
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

    def get_most_recent_metric_by_scenario(
        self,
        company_id: str,
        scenario_type: str,
        metric: str,
        value_alias: str,
    ) -> dict:
        try:
            where_condition = {
                f"{self.company_table}.id": f"'{company_id}'",
                f"{self.scenario_table}.type": f"'{scenario_type}'",
                f"{self.metric_table}.name": f"'{metric}'",
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
                    "time_period.start_at", self.query_builder.Order.DESC
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

    def get_company_comparison_data(
        self,
        company_id: str,
    ) -> dict:
        try:
            if company_id and company_id.strip():
                financial_scenarios = dict()
                metrics = [
                    {"scenario": "Actuals", "metric": "Revenue", "alias": "revenue"},
                    {"scenario": "Actuals", "metric": "Ebitda", "alias": "growth"},
                    {
                        "scenario": "Actual margin",
                        "metric": "Ebitda",
                        "alias": "ebitda_margin",
                    },
                    {
                        "scenario": "Actual vs budget",
                        "metric": "Revenue",
                        "alias": "revenue_vs_budget",
                    },
                    {
                        "scenario": "Actual vs budget",
                        "metric": "Ebitda",
                        "alias": "ebitda_vs_budget",
                    },
                    {
                        "scenario": "Actuals",
                        "metric": "Rule of 40",
                        "alias": "rule_of_40",
                    },
                ]
                for metric in metrics:
                    metric_average = self.get_most_recent_metric_by_scenario(
                        company_id,
                        metric.get("scenario"),
                        metric.get("metric"),
                        metric.get("alias"),
                    )

                    if metric_average:
                        financial_scenarios.update(metric_average)

                query = (
                    self.query_builder.add_table_name(self.company_table)
                    .add_select_conditions(
                        [
                            f"{self.company_table}.id",
                            f"{self.company_table}.name",
                            f"{self.company_table}.sector",
                            f"{self.company_table}.vertical",
                        ]
                    )
                    .add_sql_where_equal_condition(
                        {f"{self.company_table}.id": f"'{company_id}'"}
                    )
                    .build()
                    .get_query()
                )
                result = self.session.execute(query).fetchall()
                response = self.response_sql.process_query_result(result)
                response.update(financial_scenarios)
                self.session.commit()
                return response
            return dict()
        except Exception as error:
            self.logger.info(error)
            raise error

    def get_peers(
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

            query = (
                self.query_builder.add_table_name(self.company_table)
                .add_select_conditions(
                    [
                        f"{self.company_table}.id",
                        f"{self.company_table}.name",
                        f"{self.company_table}.sector",
                        f"{self.company_table}.vertical",
                        f"{self.company_table}.size_cohort",
                    ]
                )
                .add_sql_where_equal_condition(where_conditions)
                .build()
                .get_query()
            )
            results = self.session.execute(query).fetchall()
            self.session.commit()
            return self.response_sql.process_query_list_results(results)

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_peers_comparison_data(
        self,
        company_id: str,
        sectors: list,
        verticals: list,
        investor_profile: list,
        growth_profile: list,
        size: list,
    ) -> list:
        try:

            metrics = [
                {"scenario": "Actuals", "metric": "Revenue", "alias": "revenue"},
                {"scenario": "Actuals", "metric": "Ebitda", "alias": "growth"},
                {
                    "scenario": "Budgeted margin",
                    "metric": "Ebitda",
                    "alias": "ebitda_margin",
                },
                {
                    "scenario": "Actual vs budget",
                    "metric": "Revenue",
                    "alias": "revenue_vs_budget",
                },
                {
                    "scenario": "Actual vs budget",
                    "metric": "Ebitda",
                    "alias": "ebitda_vs_budget",
                },
                {
                    "scenario": "Actuals",
                    "metric": "Rule of 40",
                    "alias": "rule_of_40",
                },
            ]

            peers = self.get_peers(
                sectors, verticals, investor_profile, growth_profile, size
            )
            peers_data = []
            for peer in peers:
                if peer.get("id") != company_id:
                    peer_data = peer.copy()
                    for metric in metrics:
                        metric_average = self.get_most_recent_metric_by_scenario(
                            peer.get("id"),
                            metric.get("scenario"),
                            metric.get("metric"),
                            metric.get("alias"),
                        )
                        if metric_average:
                            peer_data.update(metric_average)

                    peers_data.append(peer_data)
            return self.response_sql.process_query_list_results(peers_data)
        except Exception as error:
            self.logger.info(error)
            raise error

    def get_rank(self, company_data: dict, peer_data: list):
        no_metrics = ["id", "name", "sector", "vertical", "size_cohort"]

        data = []
        data.extend(peer_data)
        data.append(company_data.copy())
        rank = dict()

        for key in company_data.keys():
            if key not in no_metrics:
                metric_order = sorted(
                    data, key=lambda company: company.get(key), reverse=True
                )
                index = (
                    metric_order.index(company_data) + 1
                    if company_data in metric_order
                    else -1
                )
                rank[key] = f"{index} of {len(metric_order)}"

        return rank

    def get_comparison_vs_peers(
        self,
        company_id: str,
        sectors: list,
        verticals: list,
        investor_profile: list,
        growth_profile: list,
        size: list,
        year: str,
    ) -> dict:
        try:
            company_comparison_data = self.get_company_comparison_data(company_id)
            peers_comparison_data = self.get_peers_comparison_data(
                company_id, sectors, verticals, investor_profile, growth_profile, size
            )
            rank = self.get_rank(company_comparison_data, peers_comparison_data)

            for company in peers_comparison_data:
                company["revenue"] = company.pop("size_cohort", "")

            return {
                "company_comparison_data": company_comparison_data,
                "rank": rank,
                "peers_comparison_data": peers_comparison_data,
            }
        except Exception as error:
            self.logger.info(error)
            raise error
