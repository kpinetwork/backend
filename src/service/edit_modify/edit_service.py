from collections import defaultdict
from app_names import TableNames, ScenarioNames, MetricNames, BASE_HEADERS


class EditModifyService:
    def __init__(
        self, session, query_builder, scenario_service, response_sql, logger
    ) -> None:
        self.logger = logger
        self.response_sql = response_sql
        self.session = session
        self.query_builder = query_builder
        self.scenario_service = scenario_service

    def __get_scenarios_config_names(self) -> dict:
        return {
            "scenario_id": f"{TableNames.SCENARIO}.id",
            "scenario": f"{TableNames.SCENARIO}.type",
            "metric": f"{TableNames.METRIC}.name",
            "metric_id": f"{TableNames.METRIC}.id",
        }

    def __get_companies_select_conditions(self) -> list:
        return [
            f"{TableNames.COMPANY}.id",
            f"{TableNames.COMPANY}.name",
            f"{TableNames.COMPANY}.sector",
            f"{TableNames.COMPANY}.vertical",
            f"{TableNames.COMPANY}.inves_profile_name",
            f"{TableNames.SCENARIO}.id as scenario_id",
            f"{TableNames.SCENARIO}.name as scenario",
            f"{TableNames.METRIC}.id as metric_id",
            f"{TableNames.METRIC}.name as metric",
            f"{TableNames.METRIC}.value as value",
        ]

    def __get_scenarios_conditions(
        self, company_id: str, scenario: dict, names_config: dict
    ) -> dict:
        scenario_parsed = {
            names_config[key]: value
            for key, value in scenario.items()
            if value is not None and key in names_config
        }
        scenario_type = scenario.get("scenario")
        year = scenario.get("year")

        if year and scenario_type:
            scenario_type = scenario.get("scenario")
            year = scenario.get("year")
            scenario_parsed[f"{TableNames.SCENARIO}.name"] = f"{scenario_type}-{year}"

        if company_id and company_id.strip():
            scenario_parsed[f"{TableNames.METRIC}.company_id"] = f"{company_id}"

        return self.__get_valid_conditions(scenario_parsed)

    def __get_valid_conditions(self, conditions: dict) -> dict:
        return {
            key: (f"'{value}'" if isinstance(value, str) else value)
            for key, value in conditions.items()
        }

    def __get_company_description_query(
        self, company_id: str, description: dict
    ) -> str:
        conditions = self.__get_valid_conditions(description)
        return (
            self.query_builder.add_table_name(TableNames.COMPANY)
            .add_set_conditions(conditions)
            .add_sql_where_equal_condition(
                {f"{TableNames.COMPANY}.id": f"'{company_id}'"}
            )
            .build_update()
            .get_query()
        )

    def __get_join_update_query(self, conditions: dict) -> str:
        query = (
            self.query_builder.add_table_name(TableNames.METRIC)
            .add_select_conditions([f"{TableNames.METRIC}.id as metric_id"])
            .add_join_clause(
                {
                    f"{TableNames.SCENARIO_METRIC}": {
                        "from": f"{TableNames.SCENARIO_METRIC}.metric_id",
                        "to": f"{TableNames.METRIC}.id",
                    }
                }
            )
            .add_join_clause(
                {
                    f"{TableNames.SCENARIO}": {
                        "from": f"{TableNames.SCENARIO_METRIC}.scenario_id",
                        "to": f"{TableNames.SCENARIO}.id",
                    }
                }
            )
            .add_sql_where_equal_condition(conditions)
            .build()
            .get_query()
        )

        return f"with scenario as ({query})"

    def __get_base_update_query(self, value: float) -> str:
        return (
            self.query_builder.add_table_name(TableNames.METRIC)
            .add_set_conditions({"value": value})
            .build_update()
            .get_query()
        )

    def __get_conditions_query(self, conditions: dict) -> str:
        return self.query_builder.add_sql_where_equal_condition(
            conditions
        ).get_where_query()

    def __get_update_query(
        self, join_query: str, base_query: str, from_query: str, conditions: dict
    ) -> str:
        return """
        {with_query}
        {update_query}
        {from_statement}
        {where_conditions}""".format(
            with_query=join_query,
            update_query=base_query,
            from_statement=from_query,
            where_conditions=self.__get_conditions_query(conditions),
        )

    def __get_scenario_update_query(
        self, company_id: str, scenario: dict, names_config: dict
    ) -> str:
        where_conditions = self.__get_scenarios_conditions(
            company_id, scenario, names_config
        )
        has_scenario_conditions = [
            key for key in where_conditions if TableNames.SCENARIO in key
        ]
        conditions = {f"{TableNames.METRIC}.id": f"'{scenario.get('metric_id')}'"}

        join_query = ""
        from_statement = ""
        query = self.__get_base_update_query(scenario.get("value"))

        if has_scenario_conditions:
            join_query = self.__get_join_update_query(where_conditions)
            conditions = {f"{TableNames.METRIC}.id": f"{TableNames.SCENARIO}.metric_id"}
            from_statement = f"FROM scenario as {TableNames.SCENARIO}"

        return self.__get_update_query(join_query, query, from_statement, conditions)

    def __get_company_scenarios_query(self, company_id: str, scenarios: list) -> list:
        queries = []
        names_config = self.__get_scenarios_config_names()

        for scenario in scenarios:
            query = self.__get_scenario_update_query(company_id, scenario, names_config)
            queries.append(query)

        return queries

    def __get_companies_query(self, companies: list) -> list:
        company_queries = []

        for company in companies:
            company_id = company.get("id")
            description = company.get("description")
            scenarios = company.get("scenarios")
            if description:
                company_queries.append(
                    self.__get_company_description_query(company_id, description)
                )
            if scenarios:
                company_queries.extend(
                    self.__get_company_scenarios_query(company_id, scenarios)
                )

        return company_queries

    def __get_add_scenario_response(self, scenario: dict) -> dict:
        return {
            "scenario": f"{scenario.get('scenario')}-{scenario.get('year')}",
            "metric": f"{scenario.get('metric')}",
            "added": False,
        }

    def __add_scenario(self, company_id, scenario: dict) -> dict:
        scenario_response = self.__get_add_scenario_response(scenario)
        try:
            self.scenario_service.add_company_scenario(company_id, **scenario)
            scenario_response["added"] = True
        except Exception as error:
            scenario_response["error"] = str(error)
        return scenario_response

    def __add_scenarios(self, scenarios: list) -> dict:
        added = defaultdict(list)

        for scenario in scenarios:
            company_id = scenario.pop("company_id", None)
            scenario_response = self.__add_scenario(company_id, scenario)
            added[company_id].extend([scenario_response])
        return added

    def add_data(self, scenarios: list) -> dict:
        try:
            return self.__add_scenarios(scenarios)
        except Exception as error:
            self.logger.info(error)
            return dict()

    def edit_data(self, companies: list) -> bool:
        try:
            queries = self.__get_companies_query(companies)
            query = """
                BEGIN;
                    {updates};
                COMMIT;
            """.format(
                updates=";".join(queries)
            )

            self.session.execute(query)
            self.session.commit()
            return True
        except Exception as error:
            self.logger.info(error)
            return False

    def __add_list_filters(self, table_name: str, **kwargs) -> dict:
        filters = dict()
        for k, v in kwargs.items():
            values = [f"'{element}'" for element in v if element and element.strip()]
            filters[f"{table_name}.{k}"] = values
        return filters

    def get_companies_information(self, rows: dict, filters: dict) -> dict:
        conditions = {
            f"{TableNames.COMPANY}.is_public ": True,
        }
        if filters:
            conditions.update(filters)
        try:
            query = (
                self.query_builder.add_table_name(TableNames.COMPANY)
                .add_select_conditions(self.__get_companies_select_conditions())
                .add_join_clause(
                    {
                        f"{TableNames.SCENARIO}": {
                            "from": f"{TableNames.SCENARIO}.company_id",
                            "to": f"{TableNames.COMPANY}.id",
                        }
                    }
                )
                .add_join_clause(
                    {
                        f"{TableNames.SCENARIO_METRIC}": {
                            "from": f"{TableNames.SCENARIO_METRIC}.scenario_id",
                            "to": f"{TableNames.SCENARIO}.id",
                        }
                    }
                )
                .add_join_clause(
                    {
                        f"{TableNames.METRIC}": {
                            "from": f"{TableNames.METRIC}.id",
                            "to": f"{TableNames.SCENARIO_METRIC}.metric_id",
                        }
                    }
                )
                .add_sql_where_equal_condition(conditions)
                .add_sql_order_by_condition(
                    [f"{TableNames.COMPANY}.name"],
                    self.query_builder.Order.ASC,
                )
                .build()
                .get_query()
            )
            results = self.session.execute(query).fetchall()
            self.session.commit()
            return self.__build_companies_rows(results, rows)
        except Exception as error:
            self.logger.info(error)
            return {}

    def __get_scenarios_by_type(self, scenario_type: str) -> list:
        metrics = [f"'{metric.value}'" for metric in MetricNames]
        conditions = {"s.type": f"'{scenario_type}'", "m.name": metrics}

        try:
            query = (
                self.query_builder.add_table_name(TableNames.COMPANY)
                .add_select_conditions(
                    ["DISTINCT ON(s.name, m.name) s.name as scenario, m.name as metric"]
                )
                .add_join_clause(
                    {
                        f"{TableNames.SCENARIO} s": {
                            "from": "s.company_id",
                            "to": f"{TableNames.COMPANY}.id",
                        }
                    }
                )
                .add_join_clause(
                    {
                        f"{TableNames.SCENARIO_METRIC} sm": {
                            "from": "sm.scenario_id",
                            "to": "s.id",
                        }
                    }
                )
                .add_join_clause(
                    {
                        f"{TableNames.METRIC} m": {
                            "from": "m.id",
                            "to": "sm.metric_id",
                        }
                    }
                )
                .add_sql_where_equal_condition(conditions)
                .build()
                .get_query()
            )
            results = self.session.execute(query).fetchall()
            self.session.commit()
            return self.response_sql.process_query_list_results(results)
        except Exception as error:
            self.logger.info(error)
            return []

    def __get_main_rows(self, scenarios: list) -> dict:
        headers = BASE_HEADERS.copy()
        metrics = self.__build_row(len(BASE_HEADERS))
        years = self.__build_row(len(BASE_HEADERS))

        for scenario in scenarios:
            scenarios_name = self.__process_scenarios(
                self.__get_scenarios_by_type(scenario)
            )
            headers.extend(self.__build_row(len(scenarios_name), element=str(scenario)))
            self.__update_metrics_and_years_rows(scenarios_name, metrics, years)

        return {"headers": headers, "metrics": metrics, "years": years}

    def __update_metrics_and_years_rows(
        self, scenarios, metrics: list, years: list
    ) -> None:
        for metric in MetricNames:
            filtered_years = [
                scenario[1] for scenario in scenarios if scenario[0] == metric
            ]
            years.extend(filtered_years)
            metrics.extend(self.__build_row(len(filtered_years), element=str(metric)))

    def __process_scenarios(self, scenarios: list) -> list:
        return [
            (
                scenario.get("metric"),
                scenario.get("scenario").split("-")[1],
                scenario.get("scenario").split("-")[0],
            )
            for scenario in scenarios
            if scenario.get("metric") in list(MetricNames)
        ]

    def __build_row(
        self, num_of_elements: int, default_element: object = "", element: str = None
    ) -> list:
        if num_of_elements <= 0:
            return []
        row = [default_element] * num_of_elements
        if element:
            row[0] = element
        return row

    def __is_metric_scenario_valid(self, scenario: str, metric: str) -> bool:
        return scenario in list(ScenarioNames) and metric in list(MetricNames)

    def __add_company_description(self, company: dict) -> dict:
        company_attrs = ("id", "name", "sector", "vertical", "inves_profile_name")
        return {key: company.get(key, None) for key in company_attrs}

    def __get_total_scenarios(self, years_row: list) -> int:
        return len([year for year in years_row if year and year.strip()])

    def __build_companies_rows(self, records: list, rows: dict) -> dict:
        number_of_scenarios = self.__get_total_scenarios(rows.get("years"))
        response = {}

        for record in records:
            company = dict(record)
            company_id = company.get("id")
            scenario_name = company.get("scenario").split("-")
            scenario = scenario_name[0]
            metric = company.get("metric")

            if company_id not in response.keys():
                description = self.__add_company_description(company)
                scenarios = self.__build_row(number_of_scenarios, {})
                description.update({"scenarios": scenarios})
                response[company_id] = description
            if self.__is_metric_scenario_valid(scenario, metric):
                index = self.__find_scenario_index(
                    rows,
                    number_of_scenarios,
                    metric=metric,
                    scenario=scenario,
                    year=scenario_name[1],
                )
                scenarios = response.get(company_id).get("scenarios")
                scenarios[index] = {
                    "scenario_id": company.get("scenario_id"),
                    "scenario": scenario_name[0],
                    "year": scenario_name[1],
                    "metric_id": company.get("metric_id"),
                    "metric": company.get("metric"),
                    "value": float(company.get("value")),
                }
                response.get(company_id).update({"scenarios": scenarios})

        return response

    def __slice_row(self, row: list, i_index: int, e_index: int = None) -> list:
        if e_index:
            return row[i_index:e_index]
        return row[i_index:]

    def __get_range_in_scenarios_row(
        self, scenario, actuals_index, budget_index, num_of_scenarios
    ) -> tuple:
        init_range_value = 0

        if scenario == ScenarioNames.ACTUALS:
            range_index = [actuals_index, budget_index - 1]
            init_range_value = actuals_index
        else:
            range_index = [budget_index, num_of_scenarios - 1]
            init_range_value = budget_index

        return range_index, init_range_value

    def __get_range_in_metrics_row(self, metrics, metric, range, init_range_value):
        range[0] = metrics.index(metric) + init_range_value
        if metric == MetricNames.REVENUE:
            range[1] = metrics.index(str(MetricNames.EBITDA)) + init_range_value - 1
        init_range_value = range[0]

        return range, init_range_value

    def __find_scenario_index(
        self, rows: dict, number_of_scenarios: int, **kwargs
    ) -> int:
        sliced_headers = self.__slice_row(rows.get("headers"), len(BASE_HEADERS))

        actuals_scenario_index = sliced_headers.index(str(ScenarioNames.ACTUALS))
        budget_scenario_index = sliced_headers.index(str(ScenarioNames.BUDGET))

        range_index, init_range_value = self.__get_range_in_scenarios_row(
            kwargs.get("scenario"),
            actuals_scenario_index,
            budget_scenario_index,
            number_of_scenarios,
        )

        metrics = self.__slice_row(rows.get("metrics"), len(BASE_HEADERS))
        sliced_metrics = self.__slice_row(metrics, range_index[0], range_index[1] + 1)

        range_index, init_range_value = self.__get_range_in_metrics_row(
            sliced_metrics, kwargs.get("metric"), range_index, init_range_value
        )

        years = self.__slice_row(rows.get("years"), len(BASE_HEADERS))
        sliced_years = self.__slice_row(years, range_index[0], range_index[1] + 1)

        return sliced_years.index(kwargs.get("year")) + init_range_value

    def __get_scenarios_and_filters(self, **conditions):
        scenarios = conditions.pop("scenarios", [])
        valid_names = [name.value for name in ScenarioNames]
        if scenarios:
            scenarios = [scenario for scenario in scenarios if scenario in valid_names]
        if not scenarios:
            scenarios = [scenario.value for scenario in ScenarioNames]

        scenarios_conditions = {"type": scenarios}

        filters = self.__add_list_filters(TableNames.COMPANY, **conditions)
        filters.update(
            self.__add_list_filters(TableNames.SCENARIO, **scenarios_conditions)
        )
        return (scenarios, filters)

    def edit_modify_data(self, data: dict) -> dict:
        companies = data.get("edit", [])
        scenarios = data.get("add", [])

        edited = self.edit_data(companies)
        added_scenarios = self.add_data(scenarios)

        return {"edited": edited, "added": added_scenarios}

    def get_data(self, **conditions) -> dict:
        scenarios, filters = self.__get_scenarios_and_filters(**conditions)
        rows = self.__get_main_rows(scenarios)
        companies = self.get_companies_information(rows, filters)
        rows.update({"companies": companies})

        return rows
