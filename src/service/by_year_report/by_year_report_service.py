from typing import Union

from base_metrics_repository import BaseMetricsRepository
from base_metrics_config_name import METRICS_CONFIG_NAME
from base_metrics_report import BaseMetricsReport
from app_names import MetricNames, YEAR_REPORT_ANONYMIZABLE_METRICS
from profile_range import ProfileRange


class ByYearReportService:
    def __init__(
        self,
        logger,
        report: BaseMetricsReport,
        repository: BaseMetricsRepository,
        profile_range: ProfileRange,
    ) -> None:
        self.logger = logger
        self.report = report
        self.repository = repository
        self.profile_range = profile_range

    def remove_base_metrics(self, company: dict) -> None:

        base_metrics = [
            "prior_actuals_revenue",
            "prior_actuals_new_bookings",
            "prior_actuals_run_rate_revenue",
        ]
        [
            base_metrics.extend([f"actuals_{metric}", f"budget_{metric}"])
            for metric in METRICS_CONFIG_NAME.values()
        ]

        for metric in base_metrics:
            company.pop(metric, None)

    def anonymized_companies_metrics(
        self,
        companies: dict,
        allowed_companies: list,
        profile_ranges: dict,
    ) -> None:
        for company_id in companies:
            company_data = companies[company_id]
            if company_id not in allowed_companies:
                self._anonymize_metrics_by_company(
                    company_data,
                    profile_ranges,
                )

    def _replace_metric_by_defined_ranges(
        self, company: dict, metric: str, ranges: list
    ) -> None:
        value = company.get(metric)
        value_range = self.profile_range.get_range_from_value(
            value, profile=metric, ranges=ranges
        )
        company[metric] = value_range

    def _anonymize_metrics_by_company(
        self,
        company: dict,
        profile_ranges: dict,
    ) -> None:
        for metric in YEAR_REPORT_ANONYMIZABLE_METRICS:
            self._replace_metric_by_defined_ranges(
                company, metric, profile_ranges.get(metric, [])
            )

    def get_comparison_vs_data(
        self, access: bool, data: dict, allowed_companies: list, profile_ranges: dict
    ) -> list:
        rule_of_40 = []

        for id in data:
            company_data = data[id]
            company_revenue = company_data.get("actuals_revenue")
            self.report.calculate_metrics(company_data, profile_ranges)
            if not access and id not in allowed_companies:
                self.report.anonymize_name(company_data)
            company_rule_of_40 = self.report.get_rule_of_40(
                company_data, company_revenue
            )
            if "NA" not in company_rule_of_40.values():
                rule_of_40.append(company_rule_of_40)
            self.remove_base_metrics(company_data)
        return rule_of_40

    def get_report_base_data(self, year: str, **conditions) -> dict:
        filters = self.repository.add_filters(**conditions)
        data = self.repository.get_actuals_values(year, filters)
        budget_records = self.repository.get_budget_values(
            year, [year], filters, metrics=[MetricNames.REVENUE, MetricNames.EBITDA]
        )
        prior_records = self.repository.get_prior_year_revenue_values(year, filters)

        for company_id in data:
            data[company_id].update(budget_records.get(company_id, dict()))
            data[company_id].update(prior_records.get(company_id, dict()))

        return data

    def _get_company_information_fields(self):
        information_fiels = self.repository.fields
        information_fiels.extend(["size_cohort", "margin_group"])
        return information_fiels

    def get_metric_average(self, metric_values: list) -> Union[float, str]:
        return (
            self.report.calculator.calculate_average(metric_values)
            if len(metric_values) > 0
            else "NA"
        )

    def get_valid_metric_values(self, metric: str, data: list) -> list:
        return [
            self.report.calculator.get_valid_number(company.get(metric))
            for company in data
            if company.get(metric) and company.get(metric) != "NA"
        ]

    def get_metrics_averages(self, data: list) -> dict:
        averages = dict()
        all_fields = list(data)[0].keys()
        metrics = [
            metric
            for metric in all_fields
            if metric not in self._get_company_information_fields()
        ]
        for metric in metrics:
            metric_values = self.get_valid_metric_values(metric, data)
            average = self.get_metric_average(metric_values)
            averages.update({metric: average})
        return averages

    def get_by_year_report(
        self,
        company_id: str,
        username: str,
        year: str,
        from_main: bool,
        access: bool,
        **conditions,
    ) -> dict:
        try:
            company = dict()
            is_valid_company = company_id and company_id.strip()
            self.report.set_company_permissions(username)
            allowed_companies = self.report.get_allowed_companies()
            profile_ranges = self.report.get_profiles_ranges()
            data = self.get_report_base_data(year, **conditions)

            rule_of_40 = self.get_comparison_vs_data(
                access, data, allowed_companies, profile_ranges
            )

            data = self.report.filter_by_conditions(data, **conditions)
            averages = self.get_metrics_averages(data.values())

            if not access:
                self.anonymized_companies_metrics(
                    data, allowed_companies, profile_ranges
                )

            if not from_main and is_valid_company:
                company = data.pop(company_id, dict())

            peers = self.report.get_peers_sorted(data)

            return {
                "company_comparison_data": company,
                "peers_comparison_data": peers,
                "averages": averages,
                "rule_of_40": rule_of_40,
            }
        except Exception as error:
            self.logger.info(error)
            raise error
