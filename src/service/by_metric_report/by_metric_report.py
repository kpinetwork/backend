import re
from collections import defaultdict

from app_names import ScenarioNames
from profile_range import ProfileRange
from calculator_service import CalculatorService
from company_anonymization import CompanyAnonymization
from metric_report_repository import MetricReportRepository
from base_metrics_config_name import METRICS_CONFIG_NAME, METRICS_TO_ANONYMIZE


class ByMetricReport:
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

    def get_standard_metrics(self) -> list:
        return [*self.repository.get_functions_metric(dict())]

    def get_ratio_metrics(self) -> dict:
        return {
            "clv_cac_ratio": {"decimal_places": 1},
            "cac_ratio": {"decimal_places": 2},
        }

    def build_base_metrics(self, base_metrics: list) -> list:
        metrics = [f"actuals_{metric}" for metric in base_metrics]
        metrics.extend([f"budget_{metric}" for metric in base_metrics])
        return metrics

    def get_base_metrics(self) -> list:
        base_metrics = ["gross_profit"]
        base_metrics.extend(METRICS_CONFIG_NAME.values())

        return self.build_base_metrics(base_metrics)

    def get_unrestricted_base_metrics(self) -> list:
        base_metrics = ["headcount"]
        return self.build_base_metrics(base_metrics)

    def get_growth_metrics(self, metric: str, company: dict, years: list) -> dict:
        metrics = dict()
        for year in years:
            actual = company["metrics"].get(year)
            prior = company["metrics"].get(year - 1)
            metrics[year] = (
                self.calculator.calculate_new_bookings_growth(actual, prior)
                if metric == "new_bookings_growth"
                else self.calculator.calculate_growth_rate(actual, prior)
            )
        return metrics

    def get_retention_metrics(
        self,
        metric: str,
        company_run_rate_revenue: dict,
        company_losses_and_downgrades: dict,
        company_upsells: dict,
        years: list,
    ) -> dict:
        metrics = dict()
        for year in years:
            prior_run_rate_revenue = company_run_rate_revenue["metrics"].get(year - 1)
            losses_and_downgrades = (
                company_losses_and_downgrades["metrics"].get(year)
                if company_losses_and_downgrades
                else None
            )
            if metric == "net_retention":
                upsells = (
                    company_upsells["metrics"].get(year) if company_upsells else None
                )
                metrics[year] = self.calculator.calculate_net_retention(
                    prior_run_rate_revenue, losses_and_downgrades, upsells
                )
            else:
                metrics[year] = self.calculator.calculate_gross_retention(
                    prior_run_rate_revenue, losses_and_downgrades
                )
        return metrics

    def get_rule_of_40_metrics(
        self, growth_metrics: dict, margin_metrics: dict
    ) -> dict:
        metrics = dict()
        for year in growth_metrics:
            growth = growth_metrics.get(year)
            ebitda_margin = margin_metrics.get(year)

            rule_of_40 = self.calculator.calculate_sum(growth, ebitda_margin)
            metrics[year] = rule_of_40
        return metrics

    def calculate_base_metric(self, value: float, rounded: bool = True):
        metric_value = self.calculator.calculate_base_metric(value)
        return metric_value if rounded else value

    def process_standard_metrics(self, records: list, rounded: bool = True) -> dict:
        data = defaultdict(dict)

        for record in records:
            company_id = record["id"]
            value = self.calculate_base_metric(record["value"], rounded)
            year_data = {record["year"]: value}
            company = {"id": record["id"], "name": record["name"], "metrics": year_data}
            if data.get(company_id):
                data[company_id]["metrics"].update(year_data)
            else:
                data[company_id] = company
        return data

    def process_ratio_metrics(self, metric, filters) -> dict:
        records = self.process_standard_metrics(
            self.repository.get_metric_records(metric, filters), False
        )
        for id in records.keys():
            metrics = records.get(id).get("metrics")
            for year in metrics.keys():
                value = metrics.get(year)
                if value is None:
                    metrics.update({year: "NA"})
                if value != "NA" and value is not None:
                    decimal_places = (
                        self.get_ratio_metrics().get(metric).get("decimal_places")
                    )
                    metrics.update({year: f"{value:.{decimal_places}f}x"})
        return records

    def process_growth_metrics(self, metric: str, records: list, years: list) -> dict:
        data = defaultdict(dict)
        growth = self.process_standard_metrics(records, False)
        for id in growth:
            company = growth[id]
            metrics = self.get_growth_metrics(metric, company, years)
            company = {"id": company["id"], "name": company["name"], "metrics": metrics}
            data[id] = company
        return data

    def process_retention(
        self,
        metric: str,
        run_rate_revenue: list,
        losses_and_downgrades: list,
        years: list,
        filters: list,
    ) -> dict:
        data = defaultdict(dict)
        run_rate_revenue_metrics = self.process_standard_metrics(
            run_rate_revenue, False
        )
        losses_and_downgrades_metrics = self.process_standard_metrics(
            losses_and_downgrades, False
        )
        upsells = dict()
        if metric == "net_retention":
            upsells = self.process_standard_metrics(
                self.repository.get_metric_records("actuals_upsells", filters), False
            )
        for id in run_rate_revenue_metrics:
            company = run_rate_revenue_metrics[id]
            metrics = self.get_retention_metrics(
                metric,
                run_rate_revenue_metrics.get(id),
                losses_and_downgrades_metrics.get(id, dict()),
                upsells.get(id, dict()),
                years,
            )
            company = {"id": company["id"], "name": company["name"], "metrics": metrics}
            data[id] = company
        return data

    def process_debt_ebitda(self, metric: str, filters) -> dict:
        records = self.process_standard_metrics(
            self.repository.get_metric_records(metric, filters), False
        )
        for id in records.keys():
            metrics = records.get(id).get("metrics")
            for year in metrics.keys():
                value = metrics.get(year)
                if value is None:
                    metrics.update({year: "NA"})
                if value != "NA" and value is not None:
                    metrics.update({year: float(round(value, 2))})
        return records

    def process_rule_of_40(self, data_growth: dict, data_margin: dict) -> dict:
        companies = set([*data_growth] + [*data_margin])
        default_metrics = {"metrics": {}}
        data_rule = dict()
        for id in companies:
            margin_metrics = data_margin.get(id, default_metrics)["metrics"]
            growth_metrics = data_growth.get(id, default_metrics)["metrics"]
            metrics = self.get_rule_of_40_metrics(growth_metrics, margin_metrics)
            name = (
                data_margin.get(id).get("name")
                if data_margin.get(id)
                else data_growth[id].get("name")
            )
            data_rule[id] = {"id": id, "name": name, "metrics": metrics}
        return data_rule

    def __get_revenues_values(self, revenues: list) -> dict:
        data = defaultdict(list)
        for record in revenues:
            scenario = [{"scenario": record["name"], "value": record["value"]}]
            data[record["id"]].extend(scenario)
        return data

    def __get_actuals_and_prior_revenues(self, revenues_values: list) -> tuple:
        revenues_values.extend([{}, {}])
        return tuple([record.get("value") for record in revenues_values[:2]])

    def __get_company_profiles(
        self, actuals: int, prior: int, sizes: list, growths: list
    ) -> dict:
        return {
            "size_cohort": self.profile_range.get_range_from_value(
                actuals, ranges=sizes
            ),
            "margin_group": self.profile_range.get_range_from_value(
                self.calculator.calculate_growth_rate(actuals, prior, False),
                ranges=growths,
            ),
        }

    def get_profiles(self, filters: dict) -> dict:
        revenues = self.__get_revenues_values(
            self.repository.get_most_recents_revenue(filters)
        )
        sizes = self.profile_range.get_profile_ranges("revenue")
        growths = self.profile_range.get_profile_ranges("growth")

        companies_profiles_data = defaultdict(dict)
        for company in revenues:
            actuals, prior = self.__get_actuals_and_prior_revenues(revenues[company])
            companies_profiles_data[company] = self.__get_company_profiles(
                actuals, prior, sizes, growths
            )
        return companies_profiles_data

    def get_retention_records(self, metric: str, years: list, filters: dict) -> dict:
        run_rate_revenue = self.repository.get_metric_records(
            "actuals_run_rate_revenue", filters
        )
        losses_and_downgrades = self.repository.get_metric_records(
            "actuals_losses_and_downgrades", filters
        )
        return self.process_retention(
            metric, run_rate_revenue, losses_and_downgrades, years, filters
        )

    def get_no_standard_records(self, metric: str, years: list, filters: dict) -> dict:
        if "retention" in metric:
            return self.get_retention_records(metric, years, filters)

        if metric == "new_bookings_growth":
            new_bookings = self.repository.get_metric_records(
                "actuals_new_bookings", filters
            )
            return self.process_growth_metrics(metric, new_bookings, years)

        revenue = self.repository.get_metric_records("actuals_revenue", filters)
        data_growth = self.process_growth_metrics(metric, revenue, years)
        if metric == "growth":
            return data_growth

        margin = self.repository.get_metric_records("ebitda_margin", filters)
        data_margin = self.process_standard_metrics(margin)
        return self.process_rule_of_40(data_growth, data_margin)

    def get_records(self, metric: str, years: list, filters: dict) -> dict:
        standard = self.get_standard_metrics()
        if metric in self.get_ratio_metrics().keys():
            return self.process_ratio_metrics(metric, filters)
        if metric == "debt_ebitda":
            return self.process_debt_ebitda(metric, filters)
        if metric in standard:
            records = self.repository.get_metric_records(metric, filters)
            return self.process_standard_metrics(records)
        return self.get_no_standard_records(metric, years, filters)

    def get_na_year_records(self, company: dict, years: list) -> dict:
        metric_years = [*company["metrics"]]
        not_included_years = set(metric_years) ^ set(years)
        return {year: "NA" for year in not_included_years}

    def is_in_range(self, profile: dict, **conditions) -> bool:
        size_cohort = conditions.get("size_cohort", [])
        margin_group = conditions.get("margin_group", [])
        contained = []
        if not profile:
            return False
        if size_cohort:
            contained.append(profile["size_cohort"] in size_cohort)
        if margin_group:
            contained.append(profile["margin_group"] in margin_group)

        return all(contained)

    def anonymized_name(self, id: str) -> str:
        return self.company_anonymization.anonymize_company_name(id)

    def anonymized_metric(self, metrics: dict, ranges: list) -> dict:
        return {
            year: self.profile_range.get_range_from_value(
                metrics.get(year), ranges=ranges
            )
            for year in metrics
        }

    def anonymize_company(self, company: dict, ranges: list) -> None:
        company["name"] = self.anonymized_name(company.get("id"))
        company["metrics"] = self.anonymized_metric(company.get("metrics", {}), ranges)

    def clear_metric_name(self, metric: str) -> str:
        return re.sub(
            f"{ScenarioNames.ACTUALS.lower()}_|{ScenarioNames.BUDGET.lower()}_",
            "",
            metric,
        )

    def anonymize_companies_values(self, metric: str, data: dict) -> None:
        metric = self.clear_metric_name(metric)

        metric_ranges = self.profile_range.get_profile_ranges(metric)
        for company_id in data:
            if company_id not in self.company_anonymization.companies:
                self.anonymize_company(data[company_id], metric_ranges)

    def get_by_metric_records(self, metric: str, years: list, **conditions) -> dict:
        companies = dict()
        filters = self.repository.add_filters(**conditions)
        data = self.get_records(metric, years, filters)

        companies_profiles = self.get_profiles(filters)

        for id in data:
            if self.is_in_range(companies_profiles.get(id), **conditions):
                data[id]["metrics"].update(self.get_na_year_records(data[id], years))
                companies[id] = data[id]

        return companies

    def sort_peers(self, data: dict) -> list:
        return sorted(
            list(data.values()),
            key=lambda x: (
                self.company_anonymization.is_anonymized(x.get("name", "")),
                x.get("name", "").lower(),
            ),
        )

    def get_by_metric_peers(
        self,
        company_id: str,
        username: str,
        metric: str,
        from_main: bool,
        access: bool,
        **conditions,
    ) -> dict:
        try:
            company = dict()
            is_valid_company = company_id and company_id.strip()
            self.company_anonymization.set_company_permissions(username)
            years = self.repository.get_years()
            data = self.get_by_metric_records(metric, years, **conditions)
            if not access and self.clear_metric_name(metric) in METRICS_TO_ANONYMIZE:
                self.anonymize_companies_values(metric, data)

            if not from_main and is_valid_company:
                company = data.pop(company_id, dict())

            peers = self.sort_peers(data)

            return {
                "years": years,
                "company_comparison_data": company,
                "peers_comparison_data": peers,
            }
        except Exception as error:
            self.logger.info(error)
            raise error
