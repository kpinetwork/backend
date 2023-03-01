from collections import defaultdict
from typing import Union
import numbers
from functools import reduce
from datetime import date
import operator
import statistics
import copy

from calculator_service import CalculatorService
from base_metrics_config_name import METRICS_CONFIG_NAME, METRICS_TO_ANONYMIZE
from profile_range import ProfileRange
from company_anonymization import CompanyAnonymization
from metric_report_repository import MetricReportRepository
from base_exception import AppError
from app_names import MetricNames, DEFAULT_RANGES


class QuartersReport:
    def __init__(
        self,
        logger,
        calculator: CalculatorService,
        repository: MetricReportRepository,
        profile_range: ProfileRange,
        company_anonymization: CompanyAnonymization,
    ) -> None:
        self.ranges = []
        self.logger = logger
        self.repository = repository
        self.calculator = calculator
        self.profile_range = profile_range
        self.company_anonymization = company_anonymization
        self.full_year = "Full Year"

    def get_quarters(self) -> dict:
        return {"Q1": [1, 2, 3], "Q2": [4, 5, 6], "Q3": [7, 8, 9], "Q4": [10, 11, 12]}

    def get_period_by_month(self, month: int) -> str:
        for key, value in self.get_quarters().items():
            if month in value:
                return key

    def get_year_for_ltm(self, years: list, period: str) -> list:
        ltm_year = years.copy()
        if period != "Q4":
            for year in years:
                prev_year = str(int(year) - 1)
                if prev_year not in years:
                    ltm_year.append(prev_year)
            return sorted(ltm_year)
        return ltm_year

    def build_subheaders_dict(self, period: str, years: list) -> dict:
        quarters = list(self.get_quarters().keys())
        index = quarters.index(period)
        next_index = index + 1
        quarters_for_year = quarters[:next_index]
        quarters_ltm = quarters[next_index:]
        subheaders = dict()
        for year in years:
            initial_years = years[1:]
            if years.index(year) == (len(years) - 1):
                subheaders[year] = quarters_for_year + [self.full_year]
                if len(initial_years) > 1:
                    subheaders[year].append("vs")
            elif years.index(year) == 0:
                subheaders[year] = quarters_ltm
            else:
                subheaders[year] = quarters_for_year + [self.full_year] + quarters_ltm
                if initial_years.index(year) != 0:
                    full_year_index = subheaders[year].index(self.full_year)
                    subheaders[year].insert(full_year_index + 1, "vs")
        return subheaders

    def get_header(self, subheaders_dict: dict) -> list:
        headers = ["Company"]
        for key, value in subheaders_dict.items():
            headers.extend([key] + [""] * (len(value) - 1))
        return headers

    def get_subheaders(self, subheaders_dict: dict) -> list:
        return [""] + reduce(operator.iconcat, subheaders_dict.values(), [])

    def get_headers(
        self,
        years: list,
        period: str = "Q4",
    ) -> tuple:
        subheaders_dict = self.build_subheaders_dict(period, years)
        header = self.get_header(subheaders_dict)
        subheader = self.get_subheaders(subheaders_dict)
        return header, subheader

    def get_standard_metrics(self, scenario_type, years: list) -> list:
        standard = list(
            set(
                [
                    metric
                    for metric in self.repository.get_functions_metric(
                        scenario_type, years, dict()
                    )
                ]
            )
        )
        return [
            metric.split("-")[1] if len(metric.split("-")) > 1 else metric
            for metric in standard
        ]

    def __get_ltm_full_year_base_scenarios(
        self,
        subheaders_dict,
        year,
        period,
        company_id,
        company,
        quarters_per_companies,
    ) -> dict:
        def append_quarter_data(data, year, company_id):
            if data:
                quarters_per_companies.setdefault(company_id, {}).setdefault(
                    year, []
                ).append(data)

        subheader_years = list(subheaders_dict.keys())
        year_str = str(year)
        next_year = str(year + 1)
        if year_str == subheader_years[0]:
            next_year_quarters = subheaders_dict.get(year_str, [])
            next_quarter_data = (
                self.__get_valid_value(company.get("value"))
                if period in next_year_quarters
                else None
            )
            append_quarter_data(next_quarter_data, next_year, company_id)
        elif year_str == subheader_years[-1]:
            year_quarters = subheaders_dict.get(year_str)
            quarter_data = (
                self.__get_valid_value(company.get("value"))
                if period in year_quarters
                else None
            )
            append_quarter_data(quarter_data, year_str, company_id)
        else:
            full_year_index = subheaders_dict[year_str].index(self.full_year)
            next_index = full_year_index + 1
            next_year_quarters = subheaders_dict[year_str][next_index:]
            next_quarter_data = (
                self.__get_valid_value(company.get("value"))
                if period in next_year_quarters
                else None
            )
            year_quarters = subheaders_dict[year_str][:full_year_index]
            quarter_data = (
                self.__get_valid_value(company.get("value"))
                if period in year_quarters
                else None
            )
            append_quarter_data(quarter_data, year_str, company_id)
            append_quarter_data(next_quarter_data, next_year, company_id)

    def process_metrics(
        self,
        report_type: str,
        metric: str,
        years: list,
        period: str,
        filters: dict,
        scenario_type: str = "actuals_budget",
    ) -> list:
        summary = defaultdict(lambda: defaultdict(dict))
        data = self.repository.get_quarters_year_to_year_records(
            report_type, metric, scenario_type, years, period, filters
        )
        for item in data:
            id = item["id"]
            scenario = item["scenario"]
            period_name = item["period_name"]
            value = item["value"]
            summary[id][scenario]["id"] = id
            summary[id][scenario]["name"] = item["name"]
            summary[id][scenario]["scenario"] = scenario
            summary[id][scenario]["metric"] = metric
            if value is not None:
                summary[id][scenario][period_name] = round(float(value), 2)
            else:
                summary[id][scenario][period_name] = None

        result = [value for values in summary.values() for value in values.values()]
        return result

    def get_actuals_plus_budget(
        self,
        report_type: str,
        metric: str,
        years: list,
        period: str,
        filters: dict,
        scenario_type: str = "actuals_budget",
    ) -> list:
        data = self.process_metrics(
            report_type, metric, years, period, filters, scenario_type
        )
        result = []
        for year in years:
            year_data = [
                x for x in data if str(year) in x["scenario"] and x["metric"] == metric
            ]
            for actuals in [x for x in year_data if "Actuals" in x["scenario"]]:
                budget = next(
                    (x for x in year_data if x["scenario"] == "Budget-" + str(year)),
                    None,
                )
                if budget:
                    new_data = {
                        "id": actuals["id"],
                        "name": actuals["name"],
                        "scenario": "Actuals + Budget",
                        "year": year,
                        "metric": actuals["metric"],
                    }
                    for quarter in ["Q1", "Q2", "Q3", "Q4"]:
                        if (
                            actuals.get(quarter) is None
                            and budget.get(quarter) is not None
                        ):
                            new_data[quarter] = budget[quarter]
                        elif actuals.get(quarter) is not None:
                            new_data[quarter] = actuals[quarter]
                        else:
                            new_data[quarter] = None
                    result.append(new_data)
                else:
                    actuals["scenario"] = "Actuals + Budget"
                    actuals["year"] = year
                    result.append(actuals)
        return result

    def __get_calculate_full_year_property_year_to_year(
        self, data: dict
    ) -> Union[float, None]:
        full_year = 0
        if None in [data.get("Q1"), data.get("Q2"), data.get("Q3"), data.get("Q4")]:
            full_year = None
        else:
            full_year = (
                data.get("Q1") + data.get("Q2") + data.get("Q3") + data.get("Q4")
            )

        return full_year

    def __get_calculate_full_year_property_year_to_date(
        self, data: dict, period: str
    ) -> Union[float, None]:
        full_year = 0
        quarters = ["Q1", "Q2", "Q3", "Q4"]
        period_index = quarters.index(period)
        needed_quarters = quarters[: period_index + 1]
        quarters_values = [data.get(value, 0) for value in needed_quarters]
        if None not in quarters_values:
            full_year = sum(quarters_values)
        if full_year == 0:
            return None
        return full_year

    def __split_periods_by_last_twelve_months(self):
        try:
            month = date.today().month
            period_of_month = self.get_period_by_month(month)
            periods = ["Q1", "Q2", "Q3", "Q4"]
            period_index = periods.index(period_of_month)
            next_period_index = period_index + 1
            return periods[:next_period_index], periods[next_period_index:]
        except ValueError:
            return None, None

    def add_full_year_property_last_twelve_months(
        self,
        report_type: str,
        metric: str,
        years: list,
        period: str,
        filters: dict,
        scenario_type: str = "actuals_budget",
    ) -> list:
        data = self.get_actuals_plus_budget(
            report_type, metric, years, period, filters, scenario_type
        )
        actual_periods, previous_periods = self.__split_periods_by_last_twelve_months()
        for company in data:
            full_year = 0
            company_id = company["id"]
            year = int(company["year"])
            previous_company_data = next(
                (
                    item
                    for item in data
                    if item["id"] == company_id and item["year"] == f"{year-1}"
                ),
                None,
            )
            previous_company_values = (
                [previous_company_data.get(prop, None) for prop in previous_periods]
                if previous_company_data is not None
                else [None]
            )
            if None in previous_company_values:
                full_year = None
            else:
                full_year = sum(previous_company_values)
            actual_company_values = [company.get(prop, None) for prop in actual_periods]
            if None in actual_company_values or full_year is None:
                full_year = None
            else:
                full_year += sum(actual_company_values)
            company[self.full_year] = full_year
        return data

    def add_full_year_property(
        self,
        report_type: str,
        metric: str,
        years: list,
        period: str,
        filters: dict,
        scenario_type: str = "actuals_budget",
    ) -> list:
        data = self.get_actuals_plus_budget(report_type, metric, years, period, filters)
        for item in data:
            if report_type == "year_to_date" and period != "Q4":
                full_year = self.__get_calculate_full_year_property_year_to_date(
                    item, period
                )
            else:
                full_year = self.__get_calculate_full_year_property_year_to_year(item)
            item[self.full_year] = full_year
        return data

    def is_valid_value(self, value) -> Union[float, str, None]:
        return value if value is not None else "NA"

    def add_vs_property(
        self,
        report_type: str,
        metric: str,
        years: list,
        period: str,
        filters: dict,
        scenario_type: str = "actuals_budget",
    ) -> list:
        data = []
        if report_type == "last_twelve_months":
            data = self.add_full_year_property_last_twelve_months(
                report_type, metric, years, period, filters
            )
        else:
            data = self.add_full_year_property(
                report_type, metric, years, period, filters
            )
        first_year = years[0] if report_type != "last_twelve_months" else years[1]
        companies = {}
        prev_full_year = {}
        for item in data:
            if item["id"] not in companies:
                companies[item["id"]] = {
                    "id": item["id"],
                    "name": item["name"],
                    "quarters": [],
                }
                prev_full_year[item["id"]] = None
            quarter = {
                "year": item["year"],
                "Q1": self.is_valid_value(item.get("Q1", None)),
                "Q2": self.is_valid_value(item.get("Q2", None)),
                "Q3": self.is_valid_value(item.get("Q3", None)),
                "Q4": self.is_valid_value(item.get("Q4", None)),
                self.full_year: self.is_valid_value(item.get(self.full_year, None)),
            }
            if quarter["year"] != first_year:
                if (
                    prev_full_year[item["id"]] is not None
                    and prev_full_year[item["id"]] != "NA"
                    and quarter[self.full_year] != "NA"
                ):
                    quarter["vs"] = round(
                        (quarter[self.full_year] / prev_full_year[item["id"]] * 100), 2
                    )
                else:
                    quarter["vs"] = "NA"
            prev_full_year[item["id"]] = quarter[self.full_year]
            companies[item["id"]]["quarters"].append(quarter)
        return list(companies.values())

    def filter_companies(self, companies: list, years: list) -> list:
        filtered_companies = []
        for company in companies:
            quarter_years = [quarter["year"] for quarter in company["quarters"]]
            if all(year in quarter_years for year in years):
                filtered_companies.append(company)
        return filtered_companies

    def __get_year_data(self, year, companies, is_first_year):
        def initialize_year_data(is_first_year):
            year_data = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0, self.full_year: 0}
            if not is_first_year:
                year_data["vs"] = 0
            return year_data

        def update_year_data(year_data, count, quarter):
            for key, value in quarter.items():
                if key != "year" and value != "NA":
                    year_data[key] += value
                    count[key] += 1

        year_data = initialize_year_data(is_first_year)
        count = initialize_year_data(is_first_year)

        for company in companies:
            for quarter in company["quarters"]:
                if quarter["year"] == year:
                    update_year_data(year_data, count, quarter)

        return year_data, count

    def calculate_averages(self, companies, years):
        averages = []
        first_year = True
        for year in years:
            year_data, count = self.__get_year_data(year, companies, first_year)
            year_result = {}
            for key in year_data.keys():
                if count[key] > 0:
                    year_result[key] = round((year_data[key] / count[key]), 2)
                else:
                    year_result[key] = "NA"

            for key, value in year_result.items():
                averages.append({key: value})

            first_year = False
        return averages

    def add_missing_years(self, data, years, report_type):
        first_year = years[0] if report_type != "last_twelve_months" else years[1]
        for company in data:
            company_quarters = company["quarters"]
            self.__add_missing_quarters(company_quarters, years, first_year)
            self.__sort_quarters(company_quarters)
        return data

    def __add_missing_quarters(self, company_quarters, years, first_year):
        for year in years:
            found = any(q["year"] == str(year) for q in company_quarters)
            if not found:
                quarter = self.__create_default_quarter(year, first_year)
                company_quarters.append(quarter)

    def __create_default_quarter(self, year, first_year):
        default_quarter = {
            "year": str(year),
            "Q1": "NA",
            "Q2": "NA",
            "Q3": "NA",
            "Q4": "NA",
            self.full_year: "NA",
        }
        if year != first_year:
            default_quarter["vs"] = "NA"
        return default_quarter

    def __sort_quarters(self, company_quarters):
        company_quarters.sort(key=lambda x: int(x["year"]))

    def get_records(
        self,
        report_type: str,
        metric: str,
        scenario_type: str,
        years: list,
        period: str,
        filters: dict,
    ) -> dict:
        standard = self.get_standard_metrics(scenario_type, years)
        if metric in standard:
            records = self.repository.get_metric_records_by_quarters(
                report_type, metric, scenario_type, years, period, filters
            )
            return self.process_standard_metrics(records, years, period, report_type)
        return self.get_no_standard_metric_records(
            report_type, metric, scenario_type, years, period, filters
        )

    def __build_default_quarters(self, includes_comparison: bool = False) -> dict:
        default_quarters = {
            "Q1": "NA",
            "Q2": "NA",
            "Q3": "NA",
            "Q4": "NA",
            self.full_year: "NA",
        }

        if includes_comparison:
            default_quarters.update({"vs": "NA"})
        return default_quarters

    def __build_default_average_object(self, years) -> dict:
        averages = {years[0]: self.__build_default_quarters()}
        averages.update(
            {
                year: self.__build_default_quarters(includes_comparison=True)
                for year in years[1:]
            }
        )
        return averages

    def __build_default_quarters_object(
        self, year, includes_comparison: bool = False
    ) -> dict:
        default_quarters_object = {"year": int(year)}
        default_quarters_object.update(
            self.__build_default_quarters(includes_comparison)
        )
        return default_quarters_object

    def __get_default_quarters(
        self, company: dict, years: list, full_year_count: int = 4
    ) -> list:
        default_quarters = [
            self.__build_default_quarters_object(year, includes_comparison=True)
            for year in years[1:]
        ]
        default_quarters.insert(0, self.__build_default_quarters_object(years[0]))
        index = years.index(str(company.get("year")))
        self.__update_quarters(default_quarters, index, company, full_year_count)

        return default_quarters

    def __update_quarters(
        self, quarters: list, index: int, company: dict, full_year_count: int = 4
    ) -> None:
        quarters[index].update(
            {
                company.get("period_name"): self.__get_valid_value(
                    company.get("value")
                ),
                self.full_year: self.__get_valid_value(company.get("full_year"))
                if company.get("quarters_count") == full_year_count
                else "NA",
            }
        )
        if index != 0:
            comparison_value = self.__get_comparison_percentage(index, quarters)
            quarters[index].update({"vs": comparison_value})

    def __get_comparison_percentage(self, index, quarters) -> Union[str, float]:
        prev_full_year = quarters[index - 1].get(self.full_year)
        full_year = quarters[index].get(self.full_year)
        return self.__calculate_comparison_percentage(prev_full_year, full_year)

    def __calculate_comparison_percentage(self, prev_full_year, full_year):
        try:
            if self.__is_comparison_valid(prev_full_year, full_year):
                return round((full_year / prev_full_year), 2) * 100
            return "NA"
        except Exception as error:
            self.logger.info(error)
            return "NA"

    def __is_comparison_valid(
        self, prev_full_year: Union[str, float], full_year: Union[str, float]
    ) -> bool:
        return isinstance(prev_full_year, numbers.Number) and isinstance(
            full_year, numbers.Number
        )

    def __get_valid_value(self, value: float) -> Union[float, str]:
        return round(float(value), 2) if value else "NA"

    def __get_full_year_count(self, period_type: str = None) -> int:
        periods = ["Q1", "Q2", "Q3", "Q4"]
        return periods.index(period_type) + 1 if period_type else len(periods)

    def process_standard_metrics(
        self,
        records: list,
        years: list,
        period_type: str = None,
        report_type: str = None,
        subheaders_dict: dict = None,
    ) -> dict:
        averages_dict = dict()
        data = defaultdict(dict)
        years.sort()
        averages = self.__build_default_average_object(years)
        comparison_object = {str(year): dict() for year in years}
        full_year_count = self.__get_full_year_count(period_type)
        for company in records:
            company_id = company.get("id")
            year = company.get("year")
            period = company.get("period_name")
            average = self.__get_valid_value(company.get("average"))
            full_year_average = self.__get_valid_value(company.get("full_year_average"))
            averages.get(str(year)).update(
                {period: average, self.full_year: full_year_average}
            )
            if report_type == "last_twelve_months":
                subheaders_dict = self.build_subheaders_dict(period_type, years)
                self.__get_ltm_full_year_base_scenarios(
                    subheaders_dict, year, period, company_id, company, averages_dict
                )

            if company_id not in data.keys():
                data[company_id] = {
                    "id": company.get("id"),
                    "name": company.get("name"),
                    "quarters": self.__get_default_quarters(
                        company, years, full_year_count
                    ),
                }
            else:
                quarters = data.get(company_id).get("quarters")
                self.__update_quarters(
                    quarters, years.index(str(year)), company, full_year_count
                )
                comparison = (
                    data.get(company_id)
                    .get("quarters")[years.index(str(year))]
                    .get("vs")
                )
                comparison_object[str(year)].update({company_id: comparison})
                company_updated = data.get(company_id)
                company_updated.update({"quarters": quarters})
                data.get(company_id).update(company_updated)
        if report_type == "last_twelve_months":
            full_year_ltm = self.__update_full_year_ltm(
                data, averages_dict, years, subheaders_dict
            )
            self.__update_comparison_ltm(
                data, comparison_object, years, subheaders_dict
            )
            self.__update_averages_ltm(full_year_ltm, averages)
        self.__update_averages_with_comparison(years, averages, comparison_object)
        data.update({"averages": averages})
        return dict(data)

    def __update_averages_ltm(self, full_year_ltm, averages):
        for year in full_year_ltm:
            if averages.get(year).get(self.full_year):
                averages[year][self.full_year] = (
                    self.__calculate_average(full_year_ltm.get(year))
                    if full_year_ltm.get(year)
                    else "NA"
                )

    def __update_full_year_ltm(self, data, full_year_dict, years, subheaders_dict):
        full_year_average_dict = {str(year): [] for year in years}
        for company_id in data:
            full_year_ltm = full_year_dict.get(company_id, [])
            for quarter in data.get(company_id).get("quarters"):
                current_year = str(quarter.get("year"))
                if full_year_ltm:
                    valid_quarters = [
                        quarter_value
                        for quarter_value in full_year_ltm.get(current_year, [])
                        if not isinstance(quarter_value, str)
                    ]
                    new_full_year = (
                        sum(valid_quarters) if len(valid_quarters) == 4 else "NA"
                    )
                    if new_full_year != "NA":
                        full_year_average_dict[current_year].append(new_full_year)
                else:
                    new_full_year = "NA"

                quarter.update({self.full_year: new_full_year})

                new_quarter = {
                    key: value
                    for key, value in quarter.items()
                    if key in subheaders_dict.get(current_year)
                }
                new_quarter.update({"year": current_year})
                data[company_id]["quarters"][years.index(current_year)] = new_quarter

        return full_year_average_dict

    def __update_comparison_ltm(self, data, comparison_object, years, subheaders_dict):
        for company_id in data:
            quarters = data.get(company_id).get("quarters")
            for quarter in quarters:
                current_year = str(quarter.get("year"))
                quarters_by_year = subheaders_dict.get(current_year)
                if "vs" in quarters_by_year:
                    prev_full_year = quarters[
                        years.index(str(int(current_year) - 1))
                    ].get(self.full_year)
                    curren_full_year = quarter.get(self.full_year)
                    comparison = self.__calculate_comparison_percentage(
                        prev_full_year, curren_full_year
                    )
                    data[company_id]["quarters"][years.index(current_year)].update(
                        {"vs": comparison}
                    )
                    comparison_object[current_year][company_id] = comparison

    def __update_averages_with_comparison(
        self, years: list, averages: dict, comparison_object: dict
    ) -> dict:
        for year in years[1:]:
            comparison_values = [
                comparison
                for comparison in comparison_object.get(str(year), dict()).values()
                if not isinstance(comparison, str) and comparison
            ]
            average = (
                self.__calculate_average(comparison_values)
                if comparison_values
                else "NA"
            )
            if averages:
                averages[str(year)].update({"vs": average})

    def __calculate_average(self, values: list) -> int:
        return int(reduce(lambda a, b: a + b, values) / len(values))

    def get_quarters_records(
        self,
        report_type: str,
        metric: str,
        scenario_type: str,
        years: list,
        period: str,
        **conditions,
    ) -> dict:
        filters = self.repository.add_filters(**conditions)
        data = self.get_records(
            report_type, metric, scenario_type, years, period, filters
        )
        return data

    def generate_headers(self, years):
        sorted_years = sorted(years)
        headers = ["Company"]
        subHeaders = [""]
        first_year = True
        for year in sorted_years:
            headers += [year, "", "", "", ""]
            subHeaders += ["Q1", "Q2", "Q3", "Q4", self.full_year]
            if not first_year:
                headers += [""]
                subHeaders += ["vs"]
            first_year = False
        return headers, subHeaders

    def get_actuals_or_budget_data(
        self,
        report_type: str,
        metric: str,
        scenario_type: str,
        years: str,
        period: str,
        conditions,
    ) -> tuple:
        scenario_type = scenario_type.capitalize()
        data = self.get_quarters_records(
            report_type, metric, scenario_type, years, period, **conditions
        )
        default_averages = data.pop("averages")
        peers = list(data.values())
        period = period if period is not None else "Q4"
        averages = self.__get_averages_for_base_scenarios(
            report_type, default_averages, self.build_subheaders_dict(period, years)
        )
        return peers, averages

    def __get_averages_for_base_scenarios(
        self, report_type: str, default_averages: dict, subheaders_dict: dict
    ) -> list:
        if report_type == "last_twelve_months":
            return self.__get_averages_for_actuals_or_budget_data_ltm(
                default_averages, subheaders_dict
            )
        return self.__get_averages_for_actuals_or_budget_data(default_averages)

    def actuals_budget_data(
        self,
        report_type,
        metric,
        years,
        period,
        conditions,
        scenario_type: str = "actuals_budget",
    ) -> tuple:
        sorted_years = sorted(years)
        averages = []
        filters = self.repository.add_filters(**conditions)
        peers = self.add_vs_property(report_type, metric, sorted_years, period, filters)
        self.filter_companies(peers, sorted_years)
        self.add_missing_years(peers, sorted_years, report_type)
        if report_type == "last_twelve_months":
            self.__update_peers_actuals_budget_to_ltm(
                peers, self.build_subheaders_dict(period, years)
            )
        if report_type == "last_twelve_months":
            averages = self.__get_averages_actuals_budget_ltm(
                peers, self.build_subheaders_dict(period, years)
            )
        else:
            averages = self.calculate_averages(peers, sorted_years)
        return peers, averages

    def __filter_quarter(self, quarter: dict, subheaders: dict) -> dict:
        year = quarter["year"]
        if year in subheaders:
            filtered_quarter = {"year": year}
            for key in subheaders[year]:
                if key in quarter:
                    filtered_quarter[key] = quarter[key]
            return filtered_quarter
        else:
            return {"year": year}

    def __update_company_quarters(self, data: list, subheaders: dict) -> list:
        for company in data:
            for i, quarter in enumerate(company["quarters"]):
                filtered_quarter = self.__filter_quarter(quarter, subheaders)
                company["quarters"][i] = filtered_quarter
        return data

    def __update_peers_actuals_budget_to_ltm(
        self, data: list, subheaders: dict
    ) -> list:
        return self.__update_company_quarters(data, subheaders)

    def __get_values_for_quarter_company(self, quarter, year, companies):
        return [
            quarter_company.get(quarter)
            for company in companies
            for quarter_company in company["quarters"]
            if quarter_company.get("year") == year
            and quarter_company.get(quarter) != "NA"
        ]

    def __get_average_for_quarter(self, quarter, year, companies):
        values = self.__get_values_for_quarter_company(quarter, year, companies)
        if values:
            return round(sum(values) / len(values), 2)
        return "NA"

    def __get_averages_actuals_budget_ltm(self, data: list, subheaders: list) -> list:
        averages = []
        for subheader in subheaders:
            quarter_averages = defaultdict(str)
            for quarter in subheaders[subheader]:
                quarter_averages[quarter] = self.__get_average_for_quarter(
                    quarter, subheader, data
                )
            averages.append(dict(quarter_averages))
        return averages

    def __get_averages_for_actuals_or_budget_data(self, defaul_averages: dict) -> list:
        averages = []
        for year in defaul_averages:
            for key, value in defaul_averages.get(year).items():
                averages.append({key: value})
        return averages

    def __get_averages_for_actuals_or_budget_data_ltm(
        self, defaul_averages: dict, subheaders_dict: dict = None
    ) -> list:
        averages = []
        for year in subheaders_dict.keys():
            for period in subheaders_dict.get(year):
                averages.append(
                    {period: defaul_averages.get(year, dict()).get(period, "NA")}
                )
        return averages

    def get_actuals_plus_budget_data(
        self,
        report_type: str,
        metric: str,
        years: str,
        period: str,
        conditions: dict,
        scenario_type: str,
    ):
        standard = self.get_standard_metrics(scenario_type, years)
        if metric in standard:
            return self.actuals_budget_data(
                report_type, metric, years, period, conditions, scenario_type
            )
        return self.get_no_standard_metric_records(
            report_type, metric, scenario_type, years, period, conditions
        )

    def get_peers_and_averages(
        self,
        metric: str,
        scenario_type: str,
        years: list,
        conditions,
        report_type: str = None,
        period: str = None,
    ) -> tuple:
        if scenario_type == "actuals_budget":
            peers, averages = self.get_actuals_plus_budget_data(
                report_type, metric, years, period, conditions, scenario_type
            )
        else:
            peers, averages = self.get_actuals_or_budget_data(
                report_type, metric, scenario_type, years, period, conditions
            )
        return peers, averages

    def need_to_be_anonymized(self, metric: str) -> bool:
        return (
            metric != METRICS_CONFIG_NAME.get(MetricNames.HEADCOUNT)
            and metric in METRICS_TO_ANONYMIZE.values()
        )

    def anonymize_companies_values(self, metric: str, data: dict) -> None:
        metric_ranges = self.profile_range.get_profile_ranges(metric)
        for company in data:
            if company.get("id") not in self.company_anonymization.companies:
                self.anonymize_company(company, metric_ranges, metric)

    def anonymize_company(self, company: dict, ranges: list, metric: str) -> None:
        company["name"] = self.anonymized_name(company.get("id"))
        if self.need_to_be_anonymized(metric):
            self.anonymized_metric(company.get("quarters", {}), ranges)

    def anonymized_name(self, id: str) -> str:
        return self.company_anonymization.anonymize_company_name(id)

    def anonymized_metric(self, metrics: list, ranges: list) -> list:
        keys = list(self.__build_default_quarters().keys())
        quarters = [self.__update_metric(metric, ranges, keys) for metric in metrics]
        return quarters

    def __update_metric(self, metric, ranges, keys):
        if ranges == []:
            ranges = DEFAULT_RANGES
        updated_values = {
            key: self.profile_range.get_range_from_value(metric.get(key), ranges=ranges)
            for key, value in metric.items()
            if key in keys
        }
        metric.update(updated_values)
        return metric

    def get_new_bookings_growth_records(
        self,
        scenario_type: str,
        years: list,
        filters: dict,
        report_type: str,
        period: str = "Q4",
    ):
        if scenario_type == "actuals_budget":
            base_scenario_func = self.__get_base_metric_with_no_standard_scenario
        else:
            base_scenario_func = self.__get_base_metric_with_base_scenario

        new_bookings_years = [str(int(years[0]) - 1)] + years
        new_bookings = base_scenario_func(
            "new_bookings",
            scenario_type,
            new_bookings_years,
            filters,
            report_type,
            period,
        )

        return self.process_new_bookings_growth(
            years, report_type, scenario_type, new_bookings, period
        )

    def __update_quarters_new_bookings(
        self,
        quarter,
        quarters,
        current_year,
        prior_year,
        revenue_quarters_by_company,
        averages_dict,
        report_type,
    ):
        new_bookings_current_year = self.__get_quarter_object_by_year(
            revenue_quarters_by_company, current_year
        )
        new_bookings_prev_year = self.__get_quarter_object_by_year(
            revenue_quarters_by_company, prior_year
        )

        quarters_list = [
            quarter_key
            for quarter_key in quarter.keys()
            if quarter_key in self.get_quarters().keys()
        ]
        if report_type != "last_twelve_months":
            [
                quarter.update({quarter_value: "NA"})
                for quarter_value in quarters_list
                if quarter_value not in quarters
            ]
        for quarter_value in quarters_list:
            quarter[quarter_value] = self.calculator.calculate_new_bookings_growth(
                self.__get_quarter_value(new_bookings_current_year, quarter_value),
                self.__get_quarter_value(new_bookings_prev_year, quarter_value),
            )
            averages_dict.setdefault(current_year, {}).setdefault(
                quarter_value, []
            ).append(quarter[quarter_value])

    def process_new_bookings_growth(
        self,
        years: list,
        report_type: str,
        scenario_type: str,
        new_bookings: dict,
        period: str = "Q4",
    ):
        averages_dict = dict()
        comparison_dict = dict()
        full_year_count = self.__get_full_year_count(period)
        all_quarters = list(self.get_quarters().keys())
        quarter_index = all_quarters.index(period)
        quarters = all_quarters[: quarter_index + 1]
        quarters_complement = list(set(all_quarters) - set(quarters))

        def update_quarters_data(quarter, new_bookings_quarters_by_company):
            current_year = quarter.get("year")
            prior_year = int(current_year) - 1
            if str(current_year) in years:
                self.__update_quarters_new_bookings(
                    quarter,
                    quarters,
                    current_year,
                    prior_year,
                    new_bookings_quarters_by_company,
                    averages_dict,
                    report_type,
                )
                self.__get_full_year_no_standard_metric(
                    quarter,
                    quarters,
                    report_type,
                    full_year_count,
                    averages_dict,
                    current_year,
                )

        def get_allowed_keys(report_type, quarters_complement, all_quarters):
            keys = (
                quarters_complement
                if report_type == "last_twelve_months"
                else all_quarters
            )
            return keys + ["year", "Full Year"]

        new_bookings_growth = copy.deepcopy(new_bookings)
        for company_id in new_bookings_growth:
            growth_quarters_by_company = self.get_quarters_list_by_company(
                new_bookings_growth, company_id
            )
            new_bookings_quarters_by_company = self.get_quarters_list_by_company(
                new_bookings, company_id
            )
            for quarter in growth_quarters_by_company:
                update_quarters_data(quarter, new_bookings_quarters_by_company)
            growth_quarters_by_company.pop(0)
            allowed_keys = get_allowed_keys(
                report_type, quarters_complement, all_quarters
            )
            growth_quarters_by_company[0] = {
                key: value
                for key, value in growth_quarters_by_company[0].items()
                if key in allowed_keys
            }
            if report_type == "last_twelve_months":
                growth_quarters_by_company[1].pop("vs", None)
            for index, quarter in enumerate(growth_quarters_by_company):
                self.__update_comparison_value(
                    index,
                    quarter,
                    new_bookings_growth,
                    company_id,
                    comparison_dict,
                    quarters,
                    quarters_complement,
                    averages_dict,
                    report_type,
                )
        averages = self.__calculate_averages(averages_dict)
        if report_type == "last_twelve_months":
            years = years[1:]
        self.__update_averages_with_comparison(years, averages, comparison_dict)
        new_bookings_growth.update({"averages": averages})
        if scenario_type == "actuals_budget":
            peers, averages = self.__get_peers_from_actuals_budget(
                report_type, period, years, new_bookings_growth
            )
            return peers, averages
        return new_bookings_growth

    def get_rule_of_40_records(
        self,
        scenario_type: str,
        years: list,
        filters: dict,
        report_type: str,
        period: str = "Q4",
    ):
        if scenario_type == "actuals_budget":
            base_scenario_func = self.__get_base_metric_with_no_standard_scenario
        else:
            base_scenario_func = self.__get_base_metric_with_base_scenario

        growth_metrics = self.get_growth_rate_records(
            scenario_type, years, filters, report_type, period
        )
        if scenario_type == "actuals_budget":
            growth_metrics = {record.get("id"): record for record in growth_metrics[0]}
        margin_metrics = base_scenario_func(
            "ebitda_margin",
            scenario_type,
            years,
            filters,
            report_type,
            period,
            is_calculated=True,
        )
        return self.process_rule_of_40(
            years, report_type, scenario_type, growth_metrics, margin_metrics, period
        )

    def __update_quarters_rule_of_40(
        self,
        quarter,
        quarters,
        current_year,
        margin_current_year,
        averages_dict,
        report_type,
    ):
        quarters_list = [
            quarter_key
            for quarter_key in quarter.keys()
            if quarter_key in self.get_quarters().keys()
        ]
        if report_type != "last_twelve_months":
            [
                quarter.update({quarter_value: "NA"})
                for quarter_value in quarters_list
                if quarter_value not in quarters
            ]
        for quarter_value in quarters_list:
            quarter[quarter_value] = self.calculate_rule_of_40(
                quarter[quarter_value],
                self.__get_quarter_value(margin_current_year, quarter_value),
            )
            averages_dict.setdefault(current_year, {}).setdefault(
                quarter_value, []
            ).append(quarter[quarter_value])

    def calculate_rule_of_40(self, revenue_growth, ebitda_margin):
        try:
            rule_of_40 = revenue_growth + ebitda_margin
            return round(rule_of_40)
        except Exception as error:
            self.logger.info(error)
            return "NA"

    def process_rule_of_40(
        self,
        years: list,
        report_type: str,
        scenario_type: str,
        growth: dict,
        margin: dict,
        period: str = "Q4",
    ):
        averages_dict = dict()
        comparison_dict = dict()
        full_year_count = self.__get_full_year_count(period)
        all_quarters = list(self.get_quarters().keys())
        quarter_index = all_quarters.index(period)
        quarters = all_quarters[: quarter_index + 1]
        quarters_complement = list(set(all_quarters) - set(quarters))

        def update_quarters_data(quarter):
            current_year = quarter.get("year")
            margin_current_year = self.__get_quarter_object_by_year(
                margin_company, current_year
            )
            self.__update_quarters_rule_of_40(
                quarter,
                quarters,
                current_year,
                margin_current_year,
                averages_dict,
                report_type,
            )
            self.__get_full_year_no_standard_metric(
                quarter,
                quarters,
                report_type,
                full_year_count,
                averages_dict,
                current_year,
            )

        for company_id in growth:
            growth_company = self.get_quarters_list_by_company(growth, company_id)
            margin_company = self.get_quarters_list_by_company(margin, company_id)
            for quarter in growth_company:
                update_quarters_data(quarter)

            for index, quarter in enumerate(growth_company):
                self.__update_comparison_value(
                    index,
                    quarter,
                    growth,
                    company_id,
                    comparison_dict,
                    quarters,
                    quarters_complement,
                    averages_dict,
                    report_type,
                )
        averages = self.__calculate_averages(averages_dict)
        if report_type == "last_twelve_months":
            years = years[1:]
        self.__update_averages_with_comparison(years, averages, comparison_dict)
        growth.update({"averages": averages})
        if scenario_type == "actuals_budget":
            peers, averages = self.__get_peers_from_actuals_budget(
                report_type, period, years, growth
            )
            return peers, averages
        return growth

    def get_growth_rate_records(
        self,
        scenario_type: str,
        years: list,
        filters: dict,
        report_type: str,
        period: str = "Q4",
    ):
        if scenario_type == "actuals_budget":
            base_scenario_func = self.__get_base_metric_with_no_standard_scenario
        else:
            base_scenario_func = self.__get_base_metric_with_base_scenario

        revenue_years = [str(int(years[0]) - 1)] + years
        revenue = base_scenario_func(
            "revenue", scenario_type, revenue_years, filters, report_type, period
        )

        return self.process_growth_rate(
            years, report_type, scenario_type, revenue, period
        )

    def __update_quarters_growth_rate(
        self,
        quarter,
        quarters,
        current_year,
        prior_year,
        revenue_quarters_by_company,
        averages_dict,
        report_type,
    ):
        revenue_current_year = self.__get_quarter_object_by_year(
            revenue_quarters_by_company, current_year
        )
        revenue_prev_year = self.__get_quarter_object_by_year(
            revenue_quarters_by_company, prior_year
        )

        quarters_list = [
            quarter_key
            for quarter_key in quarter.keys()
            if quarter_key in self.get_quarters().keys()
        ]
        if report_type != "last_twelve_months":
            [
                quarter.update({quarter_value: "NA"})
                for quarter_value in quarters_list
                if quarter_value not in quarters
            ]
        for quarter_value in quarters_list:
            quarter[quarter_value] = self.calculator.calculate_growth_rate(
                self.__get_quarter_value(revenue_current_year, quarter_value),
                self.__get_quarter_value(revenue_prev_year, quarter_value),
            )
            averages_dict.setdefault(current_year, {}).setdefault(
                quarter_value, []
            ).append(quarter[quarter_value])

    def process_growth_rate(
        self,
        years: list,
        report_type: str,
        scenario_type: str,
        revenue: dict,
        period: str = "Q4",
    ):
        averages_dict = dict()
        comparison_dict = dict()
        full_year_count = self.__get_full_year_count(period)
        all_quarters = list(self.get_quarters().keys())
        quarter_index = all_quarters.index(period)
        quarters = all_quarters[: quarter_index + 1]
        quarters_complement = list(set(all_quarters) - set(quarters))

        def update_quarters_data(quarter, revenue_quarters_by_company):
            current_year = quarter.get("year")
            prior_year = int(current_year) - 1
            if str(current_year) in years:
                self.__update_quarters_growth_rate(
                    quarter,
                    quarters,
                    current_year,
                    prior_year,
                    revenue_quarters_by_company,
                    averages_dict,
                    report_type,
                )
                self.__get_full_year_no_standard_metric(
                    quarter,
                    quarters,
                    report_type,
                    full_year_count,
                    averages_dict,
                    current_year,
                )

        growth = copy.deepcopy(revenue)
        for company_id in growth:
            growth_quarters_by_company = self.get_quarters_list_by_company(
                growth, company_id
            )
            revenue_quarters_by_company = self.get_quarters_list_by_company(
                revenue, company_id
            )
            for quarter in growth_quarters_by_company:
                update_quarters_data(quarter, revenue_quarters_by_company)
            growth_quarters_by_company.pop(0)
            allowed_keys = (
                quarters_complement + ["year", "Full Year"]
                if report_type == "last_twelve_months"
                else all_quarters + ["year", "Full Year"]
            )
            growth_quarters_by_company[0] = {
                key: value
                for key, value in growth_quarters_by_company[0].items()
                if key in allowed_keys
            }
            if report_type == "last_twelve_months":
                growth_quarters_by_company[1] = {
                    key: value
                    for key, value in growth_quarters_by_company[1].items()
                    if key != "vs"
                }
            for index, quarter in enumerate(growth_quarters_by_company):
                self.__update_comparison_value(
                    index,
                    quarter,
                    growth,
                    company_id,
                    comparison_dict,
                    quarters,
                    quarters_complement,
                    averages_dict,
                    report_type,
                )
        averages = self.__calculate_averages(averages_dict)
        if report_type == "last_twelve_months":
            years = years[1:]
        self.__update_averages_with_comparison(years, averages, comparison_dict)
        growth.update({"averages": averages})
        if scenario_type == "actuals_budget":
            peers, averages = self.__get_peers_from_actuals_budget(
                report_type, period, years, growth
            )
            return peers, averages
        return growth

    def __update_full_year_ltm_no_standard(
        self,
        current_year,
        prev_quarter,
        quarter,
        quarters,
        quarters_complement,
        averages_dict,
    ):
        current_quarters_values = [
            quarter_value
            for quarter_key, quarter_value in quarter.items()
            if quarter_key in quarters and isinstance(quarter_value, (int, float))
        ]
        prev_quarters_value = [
            quarter_value
            for quarter_key, quarter_value in prev_quarter.items()
            if quarter_key in quarters_complement
            and isinstance(quarter_value, (int, float))
        ]
        full_year_quarter = current_quarters_values + prev_quarters_value
        full_year = sum(full_year_quarter) if len(full_year_quarter) == 4 else "NA"
        quarter["Full Year"] = full_year
        averages_dict[current_year].setdefault("Full Year", []).append(
            quarter["Full Year"]
        )

    def __update_comparison_value(
        self,
        index: int,
        quarter: dict,
        records: list,
        company_id: str,
        comparison_dict: dict,
        quarters: list,
        quarters_complement: list,
        averages_dict: dict,
        report_type: str,
    ):
        if index != 0:
            current_year = quarter.get("year")
            prev_quarter = self.get_quarters_list_by_company(records, company_id)[
                index - 1
            ]
            if report_type == "last_twelve_months":
                self.__update_full_year_ltm_no_standard(
                    current_year,
                    prev_quarter,
                    quarter,
                    quarters,
                    quarters_complement,
                    averages_dict,
                )
            prev_full_year = prev_quarter.get("Full Year")
            current_full_year = quarter.get("Full Year")
            comparison = self.__calculate_comparison_percentage(
                prev_full_year, current_full_year
            )
            if quarter.get("vs"):
                quarter["vs"] = comparison
                comparison_dict.setdefault(str(current_year), dict()).update(
                    {company_id: quarter["vs"]}
                )

    def __get_base_metric_with_base_scenario(
        self,
        metric: str,
        scenario_type: str,
        years: list,
        filters: dict,
        report_type: str,
        period: str = "Q4",
        is_calculated: bool = False,
    ):
        metric_name = metric if is_calculated else f"{scenario_type}-{metric}"
        metric_records = self.repository.get_metric_records_with_base_scenarios(
            metric_name, scenario_type, years, filters, report_type, period
        )
        metric_data = self.process_standard_metrics(
            metric_records, years, period, report_type
        )
        metric_data.pop("averages")
        return metric_data

    def __get_base_metric_with_no_standard_scenario(
        self,
        metric: str,
        scenario_type: str,
        years: list,
        filters: dict,
        report_type: str,
        period: str = "Q4",
        is_calculated: bool = False,
    ):
        metric_data = self.actuals_budget_data(
            report_type, metric, years, period, filters, scenario_type
        )
        metric_dict = {company.get("id"): company for company in metric_data[0]}
        return metric_dict

    def get_retention_records_base_scenarios(
        self,
        metric: str,
        scenario_type: str,
        years: list,
        filters: dict,
        report_type: str,
        period: str = "Q4",
    ):
        if scenario_type == "actuals_budget":
            base_scenario_func = self.__get_base_metric_with_no_standard_scenario
        else:
            base_scenario_func = self.__get_base_metric_with_base_scenario

        run_rate_revenue_years = [str(int(years[0]) - 1)] + years[:-1]
        run_rate_revenue = base_scenario_func(
            "run_rate_revenue",
            scenario_type,
            run_rate_revenue_years,
            filters,
            report_type,
            period,
        )
        losses_and_downgrades = base_scenario_func(
            "losses_and_downgrades", scenario_type, years, filters, report_type, period
        )

        upsells = None
        if metric == "net_retention":
            upsells = base_scenario_func(
                "upsells", scenario_type, years, filters, report_type, period
            )
        return self.process_retention_metrics(
            metric,
            years,
            report_type,
            scenario_type,
            run_rate_revenue,
            losses_and_downgrades,
            upsells,
            period,
        )

    def get_quarters_list_by_company(self, records, company_id):
        return records.get(company_id, dict()).get("quarters", [])

    def __get_quarter_object_by_year(self, quarters: list, year: int) -> list:
        return [
            quarter for quarter in quarters if str(quarter.get("year")) == str(year)
        ]

    def __get_quarter_value(self, quarters: list, quarter_name: str) -> float:
        return quarters[0].get(quarter_name, "NA") if quarters else "NA"

    def __calculate_averages(self, averages_dict: dict()) -> dict():
        return {
            str(year): {
                quarter: statistics.mean(
                    [v for v in values if isinstance(v, (int, float))]
                )
                if any(isinstance(v, (int, float)) for v in values)
                else "NA"
                for quarter, values in quarters_dict.items()
            }
            for year, quarters_dict in averages_dict.items()
        }

    def __get_peers_from_actuals_budget(
        self, report_type: str, period: str, years: list, records: dict
    ):
        averages = records.pop("averages")
        years = [str(int(years[0]) - 1)] + years
        averages = self.__get_averages_for_base_scenarios(
            report_type, averages, self.build_subheaders_dict(period, years)
        )
        peers = list(records.values())
        return peers, averages

    def __get_full_year_no_standard_metric(
        self,
        quarter,
        quarters,
        report_type,
        full_year_count,
        averages_dict,
        current_year,
    ):
        list_of_quarter_values = [
            value for key, value in quarter.items() if key in quarters and value != "NA"
        ]
        if quarter.get("Full Year"):
            quarter["Full Year"] = (
                sum(list_of_quarter_values)
                if len(list_of_quarter_values) == full_year_count
                else "NA"
            )
        if report_type != "last_twelve_months":
            averages_dict[current_year].setdefault("Full Year", []).append(
                quarter["Full Year"]
            )

    def __update_quarters_retention(
        self,
        quarter,
        quarters,
        metric,
        run_rate_revenue,
        current_year,
        company_id,
        upsells,
        averages_dict,
        report_type,
    ):
        quarters_list = [
            quarter_key
            for quarter_key in quarter.keys()
            if quarter_key in self.get_quarters().keys()
        ]
        if report_type != "last_twelve_months":
            [
                quarter.update({quarter_value: "NA"})
                for quarter_value in quarters_list
                if quarter_value not in quarters
            ]
        for quarter_value in quarters_list:
            if metric == "net_retention":
                upsells_quarters = self.get_quarters_list_by_company(
                    upsells, company_id
                )
                upsells_quarters_current_year = self.__get_quarter_object_by_year(
                    upsells_quarters, current_year
                )
                quarter[quarter_value] = self.calculator.calculate_net_retention(
                    self.__get_quarter_value(run_rate_revenue, quarter_value),
                    quarter[quarter_value],
                    self.__get_quarter_value(
                        upsells_quarters_current_year, quarter_value
                    ),
                )
            else:
                quarter[quarter_value] = self.calculator.calculate_gross_retention(
                    self.__get_quarter_value(run_rate_revenue, quarter_value),
                    quarter[quarter_value],
                )
            averages_dict.setdefault(current_year, {}).setdefault(
                quarter_value, []
            ).append(quarter[quarter_value])

    def process_retention_metrics(
        self,
        metric: str,
        years: list,
        report_type: str,
        scenario: str,
        run_rate_revenue: dict,
        losses_and_downgrades: dict,
        upsells=None,
        period: str = "Q4",
    ):
        def update_quarters_with_default_value(quarter):
            quarters_list = self.get_quarters().keys()
            for quarter_value in quarters_list:
                quarter[quarter_value] = "NA"

        def update_quarters_data(quarter, quarters):
            current_year = quarter.get("year")
            prior_year = int(current_year) - 1
            run_rate_revenue_quarters = self.get_quarters_list_by_company(
                run_rate_revenue, company_id
            )
            run_rate_revenue_quarters_prior_year = self.__get_quarter_object_by_year(
                run_rate_revenue_quarters, prior_year
            )

            if run_rate_revenue_quarters_prior_year:
                self.__update_quarters_retention(
                    quarter,
                    quarters,
                    metric,
                    run_rate_revenue_quarters_prior_year,
                    current_year,
                    company_id,
                    upsells,
                    averages_dict,
                    report_type,
                )
            else:
                update_quarters_with_default_value(quarter)
            self.__get_full_year_no_standard_metric(
                quarter,
                quarters,
                report_type,
                full_year_count,
                averages_dict,
                current_year,
            )

        averages_dict = dict()
        comparison_dict = dict()
        full_year_count = self.__get_full_year_count(period)
        all_quarters = list(self.get_quarters().keys())
        quarter_index = all_quarters.index(period)
        quarters = all_quarters[: quarter_index + 1]
        quarters_complement = list(set(all_quarters) - set(quarters))

        for company_id in losses_and_downgrades:
            company_losses_and_downgrades = self.get_quarters_list_by_company(
                losses_and_downgrades, company_id
            )
            for quarter in company_losses_and_downgrades:
                update_quarters_data(quarter, quarters)
            for index, quarter in enumerate(company_losses_and_downgrades):
                self.__update_comparison_value(
                    index,
                    quarter,
                    losses_and_downgrades,
                    company_id,
                    comparison_dict,
                    quarters,
                    quarters_complement,
                    averages_dict,
                    report_type,
                )
        averages = self.__calculate_averages(averages_dict)
        if report_type == "last_twelve_months":
            years = years[1:]
        self.__update_averages_with_comparison(years, averages, comparison_dict)
        losses_and_downgrades.update({"averages": averages})
        if scenario == "actuals_budget":
            peers, averages = self.__get_peers_from_actuals_budget(
                report_type, period, years, losses_and_downgrades
            )
            return peers, averages
        return losses_and_downgrades

    def __get_arguments(
        self,
        filters: dict,
        metric: str = None,
        scenario_type: str = None,
        years: list = [],
        report_type: str = None,
        period: str = None,
    ) -> dict:
        arguments = {"filters": filters}
        optional_params = {
            "metric": metric,
            "scenario_type": scenario_type,
            "years": years,
            "report_type": report_type,
            "period": period,
        }
        arguments.update({k: v for k, v in optional_params.items() if v is not None})
        return arguments

    def get_no_standard_function_metric(
        self, scenario, years, filters, report_type, period
    ):
        metric_config = {
            "net_retention": {
                "function": self.get_retention_records_base_scenarios,
                "arguments": self.__get_arguments(
                    filters, "net_retention", scenario, years, report_type, period
                ),
            },
            "gross_retention": {
                "function": self.get_retention_records_base_scenarios,
                "arguments": self.__get_arguments(
                    filters, "gross_retention", scenario, years, report_type, period
                ),
            },
            "growth": {
                "function": self.get_growth_rate_records,
                "arguments": self.__get_arguments(
                    filters,
                    scenario_type=scenario,
                    years=years,
                    report_type=report_type,
                    period=period,
                ),
            },
            "rule_of_40": {
                "function": self.get_rule_of_40_records,
                "arguments": self.__get_arguments(
                    filters,
                    scenario_type=scenario,
                    years=years,
                    report_type=report_type,
                    period=period,
                ),
            },
            "new_bookings_growth": {
                "function": self.get_new_bookings_growth_records,
                "arguments": self.__get_arguments(
                    filters,
                    scenario_type=scenario,
                    years=years,
                    report_type=report_type,
                    period=period,
                ),
            },
        }
        return metric_config

    def get_no_standard_metric_records(
        self,
        report_type: str,
        metric: str,
        scenario_type: str,
        years: list,
        period: str,
        filters: dict,
    ) -> list:
        functions_metric = self.get_no_standard_function_metric(
            scenario_type, years, filters, report_type, period
        )
        metric_config = functions_metric.get(metric)
        if not metric_config:
            raise AppError("Metric not found")

        function = metric_config["function"]

        return function(**metric_config["arguments"])

    def get_quarters_peers(
        self,
        company_id: str,
        username: str,
        report_type: str,
        metric: str,
        scenario_type: str,
        years: list,
        period: str,
        from_main: bool,
        access: bool,
        **conditions,
    ) -> dict:
        try:
            company = dict()
            is_valid_company = company_id and company_id.strip()
            self.company_anonymization.set_company_permissions(username)
            years = sorted(years)

            if report_type == "last_twelve_months":
                month = date.today().month
                period = self.get_period_by_month(month)
                years = self.get_year_for_ltm(years, period)

            peers, averages = self.get_peers_and_averages(
                metric, scenario_type, years, conditions, report_type, period
            )

            if not access:
                self.anonymize_companies_values(metric, peers)

            if not from_main and is_valid_company:
                companies_ids = [company.get("id") for company in peers]
                if company_id in companies_ids:
                    company = peers.pop(companies_ids.index(company_id))

            headers, subheaders = (
                self.get_headers(years, period)
                if report_type == "last_twelve_months"
                else self.generate_headers(years)
            )

            return {
                "headers": headers,
                "subheaders": subheaders,
                "company_comparison_data": company,
                "peers_comparison_data": peers,
                "averages": averages,
            }
        except Exception as error:
            self.logger.info(error)
            raise error
