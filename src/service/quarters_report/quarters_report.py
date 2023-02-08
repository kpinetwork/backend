from collections import defaultdict
from typing import Union
import numbers
from functools import reduce
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

    def get_standard_metrics(self, years: list) -> list:
        return list(
            set(
                [
                    metric.split("-")[1]
                    for metric in self.repository.get_functions_metric(years, dict())
                ]
            )
        )

    def process_metrics(self, metric: str, years: list, filters: dict) -> list:
        summary = defaultdict(lambda: defaultdict(dict))
        data = self.repository.get_actuals_plus_budget_metrics_query(
            metric, years, filters
        )
        for item in data:
            id = item["id"]
            scenario = item["scenario"]
            period_name = item["period_name"]
            value = item["value"]
            summary[id][scenario]["id"] = id
            summary[id][scenario]["name"] = item["name"]
            summary[id][scenario]["scenario"] = scenario
            summary[id][scenario]["metric"] = item["metric"]
            summary[id][scenario][period_name] = float(value)

        result = [value for values in summary.values() for value in values.values()]

        return result

    def get_actuals_plus_budget(self, metric: str, years: list, filters: dict) -> list:
        data = self.process_metrics(metric, years, filters)
        result = []
        for year in years:
            year_data = [
                x
                for x in data
                if str(year) in x["scenario"] and x["metric"] == "Revenue"
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

    def add_full_year_property(self, metric: str, years: list, filters: dict) -> list:
        data = self.get_actuals_plus_budget(metric, years, filters)
        for item in data:
            quarters_values = [item.get(value, 0) for value in ["Q1", "Q2", "Q3", "Q4"]]
            item["full_year"] = sum(filter(None.__ne__, quarters_values))
        return data

    def is_valid_value(self, value) -> Union[float, str, None]:
        return value if value is not None else "NA"

    def add_vs_property(self, metric: str, years: list, filters: dict) -> list:
        data = self.add_full_year_property(metric, years, filters)
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
                "full_year": item.get("full_year"),
            }
            if prev_full_year[item["id"]] is not None:
                quarter["vs"] = round(
                    (quarter["full_year"] / prev_full_year[item["id"]] * 100), 2
                )
            prev_full_year[item["id"]] = quarter["full_year"]
            companies[item["id"]]["quarters"].append(quarter)
        return list(companies.values())

    def filter_companies(self, companies: list, years: list) -> list:
        filtered_companies = []
        for company in companies:
            quarter_years = [quarter["year"] for quarter in company["quarters"]]
            if all(year in quarter_years for year in years):
                filtered_companies.append(company)
        return filtered_companies

    def calculate_averages(self, companies, years):
        averages = []
        first_year = True
        for year in years:
            year_data = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0, "full_year": 0}
            count = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0, "full_year": 0}
            if not first_year:
                year_data["vs"] = 0
                count["vs"] = 0

            for company in companies:
                for quarter in company["quarters"]:
                    if quarter["year"] == year:
                        for key, value in quarter.items():
                            if key != "year" and value != "NA":
                                year_data[key] += value
                                count[key] += 1
            for key in year_data.keys():
                if count[key] > 0:
                    year_data[key] = round((year_data[key] / count[key]), 2)
                else:
                    year_data[key] = "NA"
                averages.append({key: year_data[key]})
            first_year = False
        averages = [
            {"Full Year": item.pop("full_year")} if "full_year" in item else item
            for item in averages
        ]
        return averages

    def add_missing_years(self, data, years):
        for company in data:
            company_quarters = company["quarters"]
            for year in years:
                found = False
                for quarter in company_quarters:
                    if quarter["year"] == str(year):
                        found = True
                        break
                if not found:
                    company_quarters.append(
                        {
                            "year": str(year),
                            "Q1": "NA",
                            "Q2": "NA",
                            "Q3": "NA",
                            "Q4": "NA",
                            "Full Year": "NA",
                            "vs": "NA",
                        }
                    )
        return data

    def get_records(
        self, metric: str, scenario_type: str, years: list, filters: dict
    ) -> dict:
        standard = self.get_standard_metrics(years)
        if metric in standard:
            records = self.repository.get_metric_records_by_quarters(
                "Year-to-year", metric, scenario_type, years, filters
            )
            return self.process_standard_metrics(records, years)

    def __build_default_quarters(
        self, includes_comparison: bool = False, is_average: bool = False
    ) -> list:
        default_quarters = {
            "Q1": "NA",
            "Q2": "NA",
            "Q3": "NA",
            "Q4": "NA",
            "full_year": "NA",
        }
        if is_average:
            default_quarters.pop("full_year")
            default_quarters.update({"Full Year": "NA"})
        if includes_comparison:
            default_quarters.update({"vs": "NA"})
        return default_quarters

    def __build_default_average_object(self, years) -> dict:
        averages = {years[0]: self.__build_default_quarters(is_average=True)}
        averages.update(
            {
                year: self.__build_default_quarters(
                    includes_comparison=True, is_average=True
                )
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

    def __get_default_quarters(self, company: dict, years: list) -> list:
        default_quarters = [
            self.__build_default_quarters_object(year, includes_comparison=True)
            for year in years[1:]
        ]
        default_quarters.insert(0, self.__build_default_quarters_object(years[0]))
        index = years.index(str(company.get("year")))
        self.__update_quarters(default_quarters, index, company)

        return default_quarters

    def __update_quarters(self, quarters: list, index: int, company: dict) -> None:
        quarters[index].update(
            {
                company.get("period_name"): self.__get_valid_value(
                    company.get("value")
                ),
                "full_year": self.__get_valid_value(company.get("full_year"))
                if company.get("quarters_count") == 4
                else "NA",
            }
        )
        if index != 0:
            comparison_value = self.__get_comparison_percentage(index, quarters)
            quarters[index].update({"vs": comparison_value})

    def __get_comparison_percentage(self, index, quarters) -> float:
        try:
            prev_full_year = quarters[index - 1].get("full_year")
            full_year = quarters[index].get("full_year")
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

    def process_standard_metrics(self, records: list, years: list) -> dict:
        data = defaultdict(dict)
        years.sort()
        averages = self.__build_default_average_object(years)
        comparison_object = {str(year): dict() for year in years}
        for company in records:
            company_id = company.get("id")
            year = company.get("year")
            period = company.get("period_name")

            average = self.__get_valid_value(company.get("average"))
            full_year_average = self.__get_valid_value(company.get("full_year_average"))
            averages.get(str(year)).update(
                {period: average, "Full Year": full_year_average}
            )

            if company_id not in data.keys():
                data[company_id] = {
                    "id": company.get("id"),
                    "name": company.get("name"),
                    "quarters": self.__get_default_quarters(company, years),
                }
            else:
                quarters = data.get(company_id).get("quarters")
                self.__update_quarters(quarters, years.index(str(year)), company)
                comparison = (
                    data.get(company_id)
                    .get("quarters")[years.index(str(year))]
                    .get("vs")
                )
                comparison_object[str(year)].update({company_id: comparison})
                company_updated = data.get(company_id)
                company_updated.update({"quarters": quarters})
                data.get(company_id).update(company_updated)

        self.__update_averages_with_comparison(years, averages, comparison_object)
        data.update({"averages": averages})

        return dict(data)

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
        self, metric: str, scenario_type: str, years: list, **conditions
    ) -> dict:
        filters = self.repository.add_filters(**conditions)
        data = self.get_records(metric, scenario_type, years, filters)
        return data

    # def sort_peers(self, data: dict) -> list:
    #     return sorted(
    #         list(data.values()),
    #         key=lambda x: (
    #             self.company_anonymization.is_anonymized(x.get("name", "")),
    #             x.get("name", "").lower(),
    #         ),
    #     )

    def generate_headers(self, years):
        sorted_years = sorted(years)
        headers = ["Company"]
        subHeaders = [""]
        first_year = True
        for year in sorted_years:
            headers += [year, "", "", "", ""]
            subHeaders += ["Q1", "Q2", "Q3", "Q4", "Full Year"]
            if not first_year:
                headers += [""]
                subHeaders += ["vs"]
            first_year = False
        return headers, subHeaders

    def get_actuals_or_budget_data(
        self, metric, scenario_type, years, conditions
    ) -> tuple:
        scenario_type = scenario_type.capitalize()
        data = self.get_quarters_records(metric, scenario_type, years, **conditions)
        default_averages = data.pop("averages")
        peers = list(data.values())
        averages = self.__get_averages_for_actuals_or_budget_data(default_averages)
        return peers, averages

    def actuals_budget_data(self, metric, years, conditions) -> tuple:
        metric_alias = self.__get_metric_name(metric)
        sorted_years = sorted(years)
        peers = self.add_vs_property(metric_alias, sorted_years, conditions)
        self.filter_companies(peers, sorted_years)
        self.add_missing_years(peers, sorted_years)
        averages = self.calculate_averages(peers, sorted_years)
        return peers, averages

    def __get_averages_for_actuals_or_budget_data(self, defaul_averages: dict) -> list:
        # cambiar esto a list comprehension
        averages = []
        for year in defaul_averages:
            for key, value in defaul_averages.get(year).items():
                averages.append({key: value})
        return averages

    def __get_metric_name(self, metric: str) -> str:
        list_of_metrics = list(METRICS_CONFIG_NAME.values())
        list_of_metrics_alias = list(METRICS_CONFIG_NAME.keys())
        index = list_of_metrics.index(metric)
        metric_alias = list_of_metrics_alias[index]
        return metric_alias

    def get_peers_and_averages(
        self, metric: str, scenario_type: str, years: list, conditions
    ) -> tuple:
        if scenario_type == "actuals_budget":
            peers, averages = self.actuals_budget_data(metric, years, conditions)
        else:
            peers, averages = self.get_actuals_or_budget_data(
                metric, scenario_type, years, conditions
            )
        return peers, averages

    def need_to_be_anonymized(self, metric: str) -> bool:  # en el by metric report
        # metric = self.clear_metric_name(metric)
        return (
            metric != METRICS_CONFIG_NAME.get(MetricNames.HEADCOUNT)
            and metric in METRICS_TO_ANONYMIZE.values()
        )

    def anonymize_companies_values(self, metric: str, data: dict) -> None:
        # metric = self.clear_metric_name(metric)
        metric_ranges = self.profile_range.get_profile_ranges(metric)
        for company in data:
            if company.get("id") not in self.company_anonymization.companies:
                self.anonymize_company(company, metric_ranges)

    def anonymize_company(self, company: dict, ranges: list) -> None:
        company["name"] = self.anonymized_name(company.get("id"))
        self.anonymized_metric(company.get("quarters", {}), ranges)
        # company["quarters"] = self.anonymized_metric(company.get("quarters", {}), ranges)

    def anonymized_name(self, id: str) -> str:
        return self.company_anonymization.anonymize_company_name(id)

    def anonymized_metric(self, metrics: list, ranges: list) -> dict:
        keys = list(self.__build_default_quarters().keys())
        quarters = [self.__update_metric(metric, ranges, keys) for metric in metrics]
        return quarters

    def __update_metric(self, metric, ranges, keys):
        updated_values = {
            key: self.profile_range.get_range_from_value(metric.get(key), ranges=ranges)
            for key in keys
        }
        metric.update(updated_values)
        return metric

    def get_quarters_peers(
        self,
        company_id: str,
        username: str,
        report_type: str,
        metric: str,
        scenario_type: str,  # Actuals, Budget, Actuals+budget
        years: list,  # ['2021', '2020', '2019']
        from_main: bool,
        access: bool,
        **conditions,
    ) -> dict:
        try:
            company = dict()
            is_valid_company = company_id and company_id.strip()
            self.company_anonymization.set_company_permissions(username)

            peers, averages = self.get_peers_and_averages(
                metric, scenario_type, years, conditions
            )

            if not access and self.need_to_be_anonymized(metric):
                self.anonymize_companies_values(metric, peers)

            if not from_main and is_valid_company:
                companies_ids = [company.get("id") for company in peers]
                companies_ids.index(company_id)
                company = peers.pop(companies_ids.index(company_id))

            headers, subheaders = self.generate_headers(years)

            return {
                "subheaders": headers,
                "headers": subheaders,
                "company_comparison_data": company,
                "peers_comparison_data": peers,
                "averages": averages,
            }
        except Exception as error:
            self.logger.info(error)
            raise error
