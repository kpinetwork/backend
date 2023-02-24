from collections import defaultdict
from typing import Union
import numbers
from functools import reduce
from datetime import date
import operator

from base_metrics_config_name import METRICS_CONFIG_NAME, METRICS_TO_ANONYMIZE
from profile_range import ProfileRange
from company_anonymization import CompanyAnonymization
from metric_report_repository import MetricReportRepository
from app_names import MetricNames


class QuartersReport:
    def __init__(
        self,
        logger,
        repository: MetricReportRepository,
        profile_range: ProfileRange,
        company_anonymization: CompanyAnonymization,
    ) -> None:
        self.ranges = []
        self.logger = logger
        self.repository = repository
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
        self, data: dict
    ) -> Union[float, None]:
        quarters_values = [data.get(value, 0) for value in ["Q1", "Q2", "Q3", "Q4"]]
        full_year = sum(filter(None.__ne__, quarters_values))
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
                full_year = self.__get_calculate_full_year_property_year_to_date(item)
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
            if full_year_ltm:
                for quarter in data.get(company_id).get("quarters"):
                    current_year = str(quarter.get("year"))
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

                    quarter.update({self.full_year: new_full_year})
                    new_quarter = {
                        key: value
                        for key, value in quarter.items()
                        if key in subheaders_dict.get(current_year)
                    }
                    new_quarter.update({"year": current_year})
                    data[company_id]["quarters"][
                        years.index(current_year)
                    ] = new_quarter
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
            comparison_object.get(str(year)).values()
            comparison_values = [
                comparison
                for comparison in comparison_object.get(str(year)).values()
                if not isinstance(comparison, str) and comparison
            ]
            average = (
                self.__calculate_average(comparison_values)
                if comparison_values
                else "NA"
            )
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
        averages = self.calculate_averages(peers, sorted_years)
        if report_type == "last_twelve_months":
            averages = self.__get_averages_actuals_budget_ltm(
                averages, self.build_subheaders_dict(period, years)
            )
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

    def __get_averages_actuals_budget_ltm(
        self, averages: list, subheaders: list
    ) -> list:
        result = []
        for year, periods_year in subheaders.items():
            for average in periods_year:
                for diccionario in averages:
                    if average in diccionario:
                        result.append({average: diccionario[average]})
                        break
        return result

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
                averages.append({period: defaul_averages.get(year).get(period)})
        return averages

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
            peers, averages = self.actuals_budget_data(
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
        updated_values = {
            key: self.profile_range.get_range_from_value(metric.get(key), ranges=ranges)
            for key, value in metric.items()
            if key in keys
        }
        metric.update(updated_values)
        return metric

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
