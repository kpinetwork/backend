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

    def get_metrics(self) -> list:
        return [
            {"scenario": "Actuals", "metric": "Revenue", "alias": "revenue"},
            {"scenario": "Actuals", "metric": "Ebitda", "alias": "growth"},
            {"scenario": "Actual margin", "metric": "Ebitda", "alias": "ebitda_margin"},
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
            {"scenario": "Actuals", "metric": "Rule of 40", "alias": "rule_of_40"},
        ]

    def remove_revenue(self, peers):
        for company in peers:
            company["revenue"] = company.pop("size_cohort", "")

    def get_company(self, company_id) -> dict:
        try:
            query = (
                self.query_builder.add_table_name(self.company_table)
                .add_select_conditions(["sector"])
                .add_sql_where_equal_condition(
                    {f"{self.company_table}.id": f"'{company_id}'"}
                )
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            self.session.commit()
            return self.response_sql.process_query_result(result)
        except Exception as error:
            self.logger.info(error)
            raise error

    def get_peers_comparison_metric(self, metric_data: dict, filters: dict) -> list:
        try:
            columns = [
                f"DISTINCT ON ({self.company_table}.id) {self.company_table}.id",
                f"{self.company_table}.name",
                f"{self.company_table}.sector",
                f"{self.company_table}.vertical",
                f"{self.company_table}.size_cohort",
                "{metric_table}.value as {alias}".format(
                    metric_table=self.metric_table,
                    alias=metric_data.get("alias", "value"),
                ),
            ]

            where_conditions = {
                f"{self.scenario_table}.type": "'{type}'".format(
                    type=metric_data.get("scenario")
                ),
                f"{self.metric_table}.name": "'{metric}'".format(
                    metric=metric_data.get("metric")
                ),
            }

            where_conditions.update(filters)

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
                .add_join_clause(
                    {
                        f"{self.time_period_table}": {
                            "from": f"{self.time_period_table}.id",
                            "to": f"{self.metric_table}.period_id",
                        }
                    }
                )
                .add_sql_where_equal_condition(where_conditions)
                .add_sql_group_by_condition(
                    [
                        f"{self.company_table}.id",
                        f"{self.company_table}.name",
                        f"{self.time_period_table}.start_at",
                        f"{self.company_table}.sector",
                        f"{self.company_table}.vertical",
                        f"{self.company_table}.size_cohort",
                        f"{self.metric_table}.value",
                    ]
                )
                .add_sql_order_by_condition(
                    [f"{self.company_table}.id", f"{self.time_period_table}.start_at"],
                    self.query_builder.Order.DESC,
                )
                .build()
                .get_query()
            )

            result = self.session.execute(query).fetchall()
            self.session.commit()
            return self.response_sql.process_query_list_results(result)
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
    ) -> dict:
        try:
            if company_id and company_id.strip():
                metrics = self.get_metrics()
                data = []
                filters = self.add_company_filters(
                    sector=sectors,
                    vertical=verticals,
                    inves_profile_name=investor_profile,
                    margin_group=growth_profile,
                    size_cohort=size,
                )

                for metric in metrics:
                    values = self.get_peers_comparison_metric(metric, filters)
                    data.extend(values)

                return self.response_sql.proccess_comparison_results(data)
            return dict()
        except Exception as error:
            self.logger.info(error)
            raise error

    def get_rank(self, company_data: dict, peer_data: list):
        company_details = ["id", "name", "sector", "vertical", "size_cohort"]
        data = [company_data.copy()]
        data.extend(peer_data)
        rank = dict()

        for key in company_data.keys():
            if key not in company_details:
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

    def get_peers_comparison(
        self,
        company_id: str,
        sectors: list,
        verticals: list,
        investor_profile: list,
        growth_profile: list,
        size: list,
    ) -> dict:
        try:
            company = self.get_company(company_id)

            if company:
                data = self.get_peers_comparison_data(
                    company_id,
                    sectors,
                    verticals,
                    investor_profile,
                    growth_profile,
                    size,
                )

                company = data.pop(company_id, dict())
                peers = list(data.values())
                rank = self.get_rank(company, peers)

                self.remove_revenue(peers)
                return {
                    "company_comparison_data": company,
                    "rank": rank,
                    "peers_comparison_data": peers,
                }
            return dict()
        except Exception as error:
            self.logger.info(error)
            raise error
