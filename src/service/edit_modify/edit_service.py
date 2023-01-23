from collections import defaultdict
from typing import Union

from edit_modify_repository import EditModifyRepository
from app_names import TableNames, ScenarioNames, BASE_HEADERS, METRIC_PERIOD_NAMES


class EditModifyService:
    def __init__(
        self,
        repository: EditModifyRepository,
        scenario_service,
        metric_service,
        logger,
    ) -> None:
        self.repository = repository
        self.logger = logger
        self.scenario_service = scenario_service
        self.metric_service = metric_service
        self.number_of_periods = 5

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

    def __add_list_filters(self, table_name: str, **kwargs) -> dict:
        filters = dict()
        for k, v in kwargs.items():
            values = [f"'{element}'" for element in v if element and element.strip()]
            filters[f"{table_name}.{k}"] = values
        return filters

    def __get_main_rows(self, scenarios: list) -> dict:
        headers = BASE_HEADERS.copy()
        metrics = self.__build_row(len(BASE_HEADERS))
        years = self.__build_row(len(BASE_HEADERS))
        periods = self.__build_row(len(BASE_HEADERS))

        for scenario in scenarios:
            scenarios_name = self.__process_scenarios(
                self.repository.get_scenarios_by_type(scenario)
            )
            headers.extend(
                self.__build_row(
                    len(scenarios_name) * self.number_of_periods, element=str(scenario)
                )
            )
            self.__update_metrics_and_years_rows(scenarios_name, metrics, years)
        self.__get_periods_row(len(list(filter(None, years))), periods)
        return {
            "headers": headers,
            "metrics": metrics,
            "years": years,
            "periods": periods,
        }

    def __get_periods_row(self, num_of_elements: int, periods_row) -> list:
        periods = [period.get("period_name") for period in METRIC_PERIOD_NAMES]
        periods_row.extend(periods * num_of_elements)

    def __update_metrics_and_years_rows(
        self, scenarios, metrics: list, years: list
    ) -> None:
        for metric in self.metric_service.get_metric_types():
            filtered_years = [
                scenario[1] for scenario in scenarios if scenario[0] == metric
            ]
            for year in filtered_years:
                years.extend(
                    self.__build_row(self.number_of_periods, element=str(year))
                )
            metrics.extend(
                self.__build_row(
                    self.number_of_periods * len(filtered_years), element=str(metric)
                )
            )

    def __process_scenarios(self, scenarios: list) -> list:
        return [
            (
                scenario.get("metric"),
                scenario.get("scenario").split("-")[1],
                scenario.get("scenario").split("-")[0],
            )
            for scenario in scenarios
            if scenario.get("metric") in self.metric_service.get_metric_types()
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
        return (
            scenario in list(ScenarioNames)
            and metric in self.metric_service.get_metric_types()
        )

    def __add_company_description(self, company: dict) -> dict:
        company_attrs = ("id", "name", "sector", "vertical", "inves_profile_name")
        return {key: company.get(key, None) for key in company_attrs}

    def __get_actuals_and_budget_index(self, rows: dict) -> tuple:
        sliced_headers = self.__slice_row(rows.get("headers"), len(BASE_HEADERS))
        actuals = self.__get_elem_index(str(ScenarioNames.ACTUALS), sliced_headers)
        budget = self.__get_elem_index(str(ScenarioNames.BUDGET), sliced_headers)
        return actuals, budget

    def __build_companies_rows(self, records: list, rows: dict) -> dict:
        number_of_scenarios = len(rows.get("years"))
        (
            actuals_scenario_index,
            budget_scenario_index,
        ) = self.__get_actuals_and_budget_index(rows)
        response = dict()
        for company in records:
            company_id = company.get("id")
            scenario_name = company.get("scenario").split("-")
            scenario = scenario_name[0]
            metric = company.get("metric")
            period = company.get("period")

            if company_id not in response.keys():
                description = self.__add_company_description(company)
                scenarios = self.__build_row(number_of_scenarios, {})
                description.update({"scenarios": scenarios})
                response[company_id] = description
            if self.__is_metric_scenario_valid(scenario, metric):
                index = self.__find_scenario_index(
                    rows,
                    number_of_scenarios,
                    actuals_scenario_index,
                    budget_scenario_index,
                    metric=metric,
                    scenario=scenario,
                    year=scenario_name[1],
                    period=period,
                )
                scenarios = response.get(company_id).get("scenarios")
                scenarios[index] = {
                    "scenario_id": company.get("scenario_id"),
                    "scenario": scenario_name[0],
                    "year": scenario_name[1],
                    "metric_id": company.get("metric_id"),
                    "metric": company.get("metric"),
                    "value": float(company.get("value")),
                    "period": period,
                }
                response.get(company_id).update({"scenarios": scenarios})

        return response

    def __slice_row(self, row: list, i_index: int, e_index: int = None) -> list:
        if e_index:
            return row[i_index:e_index]
        return row[i_index:]

    def __get_range_in_scenarios_row(
        self,
        scenario: str,
        actuals_index: int,
        budget_index: int,
        num_of_scenarios: int,
    ) -> tuple:
        init_range_value = 0

        if scenario == ScenarioNames.ACTUALS:
            budget_index = (
                budget_index if budget_index is not None else num_of_scenarios
            )
            range_index = [actuals_index, budget_index - 1]
            init_range_value = actuals_index
        else:
            range_index = [budget_index, num_of_scenarios - 1]
            init_range_value = budget_index

        return range_index, init_range_value

    def __get_range_in_metrics_row(
        self, metrics: list, metric: str, range: list, init_range_value: int
    ) -> tuple:
        range[0] = metrics.index(metric) + init_range_value
        metrics_indexes = [
            i
            for i, metric in enumerate(self.__slice_row(metrics, metrics.index(metric)))
            if metric.strip()
        ]
        init_range_value = range[0]

        if len(metrics_indexes) == 1:
            range[1] = len(metrics) + init_range_value - 1
        else:
            range[1] = metrics_indexes[1] + range[0] - 1

        return range, init_range_value

    def __get_elem_index(self, elem: str, elem_list: list) -> Union[int, None]:
        return elem_list.index(elem) if elem in elem_list else None

    def __find_scenario_index(
        self,
        rows: dict,
        number_of_scenarios: int,
        actuals_scenario_index: int,
        budget_scenario_index: int,
        **kwargs,
    ) -> int:
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
        periods = self.__slice_row(rows.get("periods"), len(BASE_HEADERS))
        sliced_years = self.__slice_row(years, range_index[0], range_index[1] + 1)
        year_index = sliced_years.index(kwargs.get("year")) + init_range_value
        sliced_periods = self.__slice_row(
            periods, year_index, year_index + self.number_of_periods
        )
        init_range_value = year_index

        return (
            sliced_periods.index(kwargs.get("period", "Full-year")) + init_range_value
        )

    def __get_scenarios_and_filters(self, **conditions):
        scenarios = conditions.pop("scenarios", [])
        valid_names = [name.value for name in ScenarioNames]
        if scenarios:
            scenarios = [scenario for scenario in scenarios if scenario in valid_names]
        if not scenarios:
            scenarios = [scenario.value for scenario in ScenarioNames]

        scenarios.sort()
        scenarios_conditions = {"type": scenarios}

        filters = self.__add_list_filters(TableNames.COMPANY, **conditions)
        filters.update(
            self.__add_list_filters(TableNames.SCENARIO, **scenarios_conditions)
        )
        return (scenarios, filters)

    def edit_modify_data(self, data: dict) -> dict:
        companies = data.get("edit", [])
        scenarios = data.get("add", [])

        edited = self.repository.edit_data(companies)
        added_scenarios = self.add_data(scenarios)

        return {"edited": edited, "added": added_scenarios}

    def get_data(self, **conditions) -> dict:
        scenarios, filters = self.__get_scenarios_and_filters(**conditions)
        rows = self.__get_main_rows(scenarios)
        data = self.repository.get_companies_records(filters)
        companies_rows = self.__build_companies_rows(data, rows)
        rows.update({"companies": companies_rows})

        return rows
