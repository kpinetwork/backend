from collections import Counter


class PreviewDataValidationService:
    def __init__(self, session, query_builder, logger, response_sql) -> None:
        self.logger = logger
        self.table_name = "company"
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.logger = logger

    def __get_scenario_name(self, scenario_type: str, year: str) -> str:
        return f"{scenario_type}-{year}"

    def __get_scenarios_to_validate(self, company: dict) -> list:
        return [
            self.__get_scenario_name(scenario_type, year)
            for scenario_type in company.get("scenarios").keys()
            for year in company.get("scenarios")[scenario_type]
        ]

    def __get_metrics_to_validate(self, scenario_name: str, company: dict) -> list:
        return company["scenarios"][scenario_name.split("-")[0]][
            scenario_name.split("-")[1]
        ]

    def __get_duplicated_values(self, companies: list, key: str) -> dict:
        counts = dict(
            Counter([company.get(key) for company in companies if company.get(key)])
        )
        duplicates = {key: value for key, value in counts.items() if value > 1}

        return duplicates

    def __validate_company_metrics(
        self, scenario_to_validate: str, company_to_validate: dict, companies: dict
    ) -> dict:

        metrics_to_validate = self.__get_metrics_to_validate(
            scenario_to_validate, company_to_validate
        )
        metrics = companies[company_to_validate.get("company_id")]["scenarios"][
            scenario_to_validate
        ]
        metrics_intersection = list(set(metrics_to_validate).intersection(metrics))

        validated_metrics = dict.fromkeys(metrics_to_validate, False)
        existing_metrics = dict.fromkeys(metrics_intersection, True)
        validated_metrics.update(existing_metrics)

        return validated_metrics

    def __validate_company_scenarios(
        self, company_to_validate: dict, companies: dict
    ) -> dict():
        company_id = company_to_validate.get("company_id")
        scenarios = [scenario for scenario in companies[company_id]["scenarios"]]
        scenarios_to_validate = self.__get_scenarios_to_validate(company_to_validate)
        validated_scenarios = dict()

        for scenario_to_validate in scenarios_to_validate:
            validated_scenarios.update({scenario_to_validate: []})

            if scenario_to_validate in scenarios:
                validated_metrics = self.__validate_company_metrics(
                    scenario_to_validate, company_to_validate, companies
                )
                validated_scenarios.update({scenario_to_validate: validated_metrics})

            else:
                validated_scenarios.update(
                    {
                        scenario_to_validate: dict.fromkeys(
                            self.__get_metrics_to_validate(
                                scenario_to_validate, company_to_validate
                            ),
                            False,
                        )
                    }
                )

        return validated_scenarios

    def get_companies_data(self) -> list:
        try:
            query = (
                self.query_builder.add_table_name(self.table_name)
                .add_select_conditions(
                    [
                        f"{self.table_name}.id",
                        f"{self.table_name}.name",
                        "financial_scenario.name as scenario",
                        "metric.name as metric",
                    ]
                )
                .add_join_clause(
                    {
                        "financial_scenario": {
                            "from": f"{self.table_name}.id",
                            "to": "financial_scenario.company_id",
                        }
                    },
                    self.query_builder.JoinType.LEFT,
                )
                .add_join_clause(
                    {
                        "scenario_metric": {
                            "from": "financial_scenario.id",
                            "to": "scenario_metric.scenario_id",
                        }
                    },
                    self.query_builder.JoinType.LEFT,
                )
                .add_join_clause(
                    {
                        "metric": {
                            "from": "scenario_metric.metric_id",
                            "to": "metric.id",
                        }
                    },
                    self.query_builder.JoinType.LEFT,
                )
                .add_sql_order_by_condition(
                    [f"{self.table_name}.name"], self.query_builder.Order.ASC
                )
                .build()
                .get_query()
            )
            results = self.session.execute(query).fetchall()
            self.session.commit()
            companies = (
                self.response_sql.process_companies_data_with_financial_information(
                    results
                )
            )

            return companies

        except Exception as error:
            self.logger.info(error)
            raise error

    def validate_companies_data(self, companies_to_validate: list) -> dict:
        try:
            companies = self.get_companies_data()
            companies_ids = companies.keys()
            companies_names = [
                companies[id].get("company_name") for id in companies_ids
            ]

            existing_names = []
            validated_companies = []
            validated_ids = [
                company.get("company_id") for company in validated_companies
            ]

            for company in companies_to_validate:
                company_id, company_name = company.get("company_id", ""), company.get(
                    "company_name", ""
                )

                if company_id in companies_ids and company_id not in validated_ids:
                    validated_scenarios = self.__validate_company_scenarios(
                        company, companies
                    )
                    validated_companies.append(
                        {**company, "scenarios": validated_scenarios}
                    )

                elif (
                    company_name in companies_names
                    and company_name not in existing_names
                ):
                    existing_names.append(company.get("company_name", ""))

            return {
                "repeated_ids": self.__get_duplicated_values(
                    companies_to_validate, "company_id"
                ),
                "repeated_names": self.__get_duplicated_values(
                    companies_to_validate, "company_name"
                ),
                "existing_names": existing_names,
                "validated_companies": validated_companies,
            }
        except Exception as error:
            self.logger.info(error)
            raise error
