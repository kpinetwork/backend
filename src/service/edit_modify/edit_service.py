from collections import defaultdict
from app_names import TableNames


class EditModifyService:
    def __init__(self, session, query_builder, scenario_service, logger) -> None:
        self.logger = logger
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

    def edit_modify_data(self, data: dict) -> dict:
        companies = data.get("edit", [])
        scenarios = data.get("add", [])

        edited = self.edit_data(companies)
        added_scenarios = self.add_data(scenarios)

        return {"edited": edited, "added": added_scenarios}
