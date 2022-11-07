from app_names import COMPARISON_METRICS, ScenarioNames, MetricNames
from by_metric_report import ByMetricReport
from by_year_report_service import ByYearReportService
from base_metrics_repository import BaseMetricsRepository
from profile_range import ProfileRange
from base_metrics_config_name import METRICS_TO_ANONYMIZE


class DynamicReport:
    def __init__(
        self,
        logger,
        metric_report: ByMetricReport,
        calendar_report: ByYearReportService,
        by_year_repository: BaseMetricsRepository,
        profile_range: ProfileRange,
    ) -> None:
        self.logger = logger
        self.metric_report = metric_report
        self.calendar_report = calendar_report
        self.by_year_repository = by_year_repository
        self.profile_range = profile_range

    def __remove_scenario_type_in_metric(self, metric: str) -> str:
        for scenario in [name.value.lower() for name in ScenarioNames]:
            metric = (
                metric.replace(f"{scenario}_", "") if scenario in metric else metric
            )
        return metric

    def get_base_metrics(
        self,
        year: int,
        **conditions,
    ) -> dict:
        filters = self.by_year_repository.add_filters(**conditions)

        data = self.by_year_repository.get_actuals_values(year, filters)
        budget_values = self.by_year_repository.get_budget_values(year, [year], filters)
        prior_actuals_values = self.by_year_repository.get_prior_year_revenue_values(
            year, filters
        )

        companies = set([*data]).union([*budget_values])

        for company_id in companies:
            data[company_id].update(budget_values.get(company_id, dict()))
            data[company_id].update(prior_actuals_values.get(company_id, dict()))

        return data

    def remove_fields(self, company_data: dict, headers: list) -> None:
        company_data.pop("prior_actuals_revenue", None)
        header = ["id", "size_cohort", "margin_group"]
        header.extend(headers)
        to_delete = set(company_data.keys()).difference(header)
        for field in to_delete:
            company_data.pop(field, None)

    def replace_base_input_values(self, company_data: dict, headers: list) -> None:
        metrics = self.metric_report.get_base_metrics()
        for metric in metrics:
            if "gross_profit" not in metric and metric in company_data:
                company_data[metric] = self.metric_report.calculate_base_metric(
                    company_data.get(metric)
                )
        self.remove_fields(company_data, headers)

    def anonymize_company(
        self,
        metrics: list,
        anonymizable_metrics: list,
        profiles: dict,
        company_data: dict,
    ) -> None:
        for metric in metrics:
            value = company_data.get(metric)
            metric_name = self.__remove_scenario_type_in_metric(metric)
            if metric_name in anonymizable_metrics:
                company_data[metric] = self.profile_range.get_range_from_value(
                    value, ranges=profiles.get(metric_name, [])
                )
            company_data["name"] = self.metric_report.anonymized_name(
                company_data.get("id")
            )

    def anonymize_data(self, metrics: list, data: dict, profiles: dict) -> None:
        allowed_companies = self.calendar_report.report.get_allowed_companies()
        anonymizable_metrics = [
            metric
            for metric in METRICS_TO_ANONYMIZE.values()
            if metric != METRICS_TO_ANONYMIZE.get(MetricNames.HEADCOUNT)
        ]

        for company_id in data:
            if company_id not in allowed_companies:
                self.anonymize_company(
                    metrics, anonymizable_metrics, profiles, data[company_id]
                )

    def add_metrics(self, data: dict, headers: list, profiles: dict) -> list:
        for company_id in data:
            company_data = data[company_id]
            self.calendar_report.report.calculate_metrics(company_data, profiles)
            self.replace_base_input_values(company_data, headers)

    def get_year_report(
        self,
        company_id: str,
        username: str,
        data: dict,
        from_main: bool,
        access: bool,
        metrics: list,
        **conditions,
    ) -> dict:
        try:
            company = dict()
            is_valid_company = company_id and company_id.strip()
            headers = ["name"]
            if not metrics:
                metrics = COMPARISON_METRICS.copy()
            headers.extend(metrics)
            self.calendar_report.report.set_company_permissions(username)
            profiles = self.calendar_report.report.get_profiles_ranges()
            self.add_metrics(data, headers, profiles)
            if not access:
                self.anonymize_data(metrics, data, profiles)
            data = self.calendar_report.report.filter_by_conditions(data, **conditions)

            if not from_main and is_valid_company:
                company = data.pop(company_id, dict())

            peers = self.calendar_report.report.get_peers_sorted(data)

            return {
                "headers": headers,
                "company_comparison_data": company,
                "peers_comparison_data": peers,
            }
        except Exception as error:
            self.logger.info(error)
            raise error

    def get_dynamic_calendar_year_report(
        self,
        company_id: str,
        username: str,
        year: str,
        from_main: bool,
        access: bool,
        metrics: list,
        **conditions,
    ) -> dict:
        data = self.get_base_metrics(year=year, **conditions)
        return self.get_year_report(
            company_id, username, data, from_main, access, metrics, **conditions
        )

    def get_dynamic_report(
        self,
        company_id: str,
        username: str,
        metrics: list,
        calendar_year: int,
        from_main: bool,
        access: bool,
        **conditions,
    ) -> dict:
        try:
            if calendar_year is not None:
                return self.get_dynamic_calendar_year_report(
                    company_id,
                    username,
                    calendar_year,
                    from_main,
                    access,
                    metrics,
                    **conditions,
                )

            return {
                "headers": [],
                "company_comparison_data": {},
                "peers_comparison_data": [],
            }
        except Exception as error:
            self.logger.info(error)
            raise error
