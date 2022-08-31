from app_names import COMPARISON_METRICS
from by_metric_report import ByMetricReport
from investment_year_report import InvestmentYearReport
from comparison_vs_peers_service import ComparisonvsPeersService
from calculator_repository import CalculatorRepository
from profile_range import ProfileRange


class DynamicReport:
    def __init__(
        self,
        logger,
        metric_report: ByMetricReport,
        investment_report: InvestmentYearReport,
        calendar_report: ComparisonvsPeersService,
        by_year_repository: CalculatorRepository,
        profile_range: ProfileRange,
    ) -> None:
        self.logger = logger
        self.metric_report = metric_report
        self.investment_report = investment_report
        self.calendar_report = calendar_report
        self.by_year_repository = by_year_repository
        self.profile_range = profile_range

    def get_base_metrics(
        self,
        year: int,
        company_id: str = None,
        **conditions,
    ) -> dict:
        filters = self.by_year_repository.add_company_filters(**conditions)
        metric_options = self.by_year_repository.get_base_metrics_options(
            year=year,
            need_next_year=False,
            need_actuals_prior_year=True,
            need_budget_prior_year=False,
        )
        data = []
        for metric in metric_options:
            base_metric = self.by_year_repository.get_metric_by_scenario(
                metric.get("scenario"),
                metric.get("metric"),
                metric.get("alias"),
                company_id,
                filters,
                True,
            )
            data.extend(base_metric)

        return self.by_year_repository.process_base_data(data)

    def remove_fields(self, company_data: dict, headers: list) -> None:
        company_data.pop("prior_actuals_revenue", None)
        header = ["id"]
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

    def get_metrics_for_dynamic_ranges(self, metrics: list) -> list:
        restricted_base_metrics = list(
            set(self.metric_report.get_base_metrics())
            - set(self.metric_report.get_unrestricted_base_metrics())
        )
        restricted_base_metrics.extend(
            ["gross_profit", "revenue", "growth", "revenue_per_employee"]
        )
        return list(set(restricted_base_metrics) & set(metrics))

    def get_dynamic_range(self, metric: str, data: dict) -> list:
        values = [data[company_id].get(metric) for company_id in data]
        return self.profile_range.build_ranges_from_values(values)

    def get_dynamic_ranges(self, metrics: list, data: dict) -> dict:
        dyanmic_ranges = dict()
        for metric in metrics:
            dyanmic_ranges[metric] = self.get_dynamic_range(metric, data)

        return dyanmic_ranges

    def anonymize_company(
        self, metrics: list, ranges: dict, profiles: dict, company_data: dict
    ) -> None:
        for metric in metrics:
            value = company_data.get(metric)
            if metric == "actuals_revenue" or metric == "budget_revenue":
                company_data[metric] = self.profile_range.get_range_from_value(
                    value, ranges=profiles.get("revenue", [])
                )
            elif metric == "revenue_per_employee":
                company_data[metric] = self.profile_range.get_range_from_value(
                    value, ranges=profiles.get("revenue_per_employee", [])
                )
            elif metric == "growth":
                company_data[metric] = self.profile_range.get_range_from_value(
                    value, ranges=profiles.get("growth", [])
                )
            else:
                company_data[metric] = self.profile_range.get_range_from_value(
                    value, ranges=ranges.get(metric, [])
                )
            company_data["name"] = self.metric_report.anonymized_name(
                company_data.get("id")
            )

    def anonymize_data(self, metrics: list, data: dict, access: bool = False) -> None:
        allowed_companies = self.calendar_report.report.get_allowed_companies()
        profiles = {
            "revenue": self.profile_range.get_profile_ranges("size profile"),
            "growth": self.profile_range.get_profile_ranges("growth profile"),
            "revenue_per_employee": self.profile_range.get_profile_ranges(
                "revenue per employee"
            ),
        }
        metrics_for_ranges = self.get_metrics_for_dynamic_ranges(metrics)
        ranges = self.get_dynamic_ranges(metrics_for_ranges, data)

        for company_id in data:
            if not access and company_id not in allowed_companies:
                self.anonymize_company(
                    metrics_for_ranges, ranges, profiles, data[company_id]
                )

    def add_metrics(self, data: dict, headers: list) -> list:
        for company_id in data:
            company_data = data[company_id]
            self.calendar_report.report.calculate_metrics(company_data)
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
            self.add_metrics(data, headers)
            self.anonymize_data(metrics, data, access)
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
        data = self.get_base_metrics(year=year, company_id=company_id, **conditions)
        return self.get_year_report(
            company_id, username, data, from_main, access, metrics, **conditions
        )

    def get_dynamic_investment_year_report(
        self,
        company_id: str,
        invest_year: int,
        username: str,
        from_main: bool,
        metrics: list,
        access: bool,
        **conditions,
    ) -> dict:
        data = self.investment_report.repository.get_base_metrics(
            invest_year, **conditions
        )
        return self.get_year_report(
            company_id, username, data, from_main, access, metrics, **conditions
        )

    def get_dynamic_report(
        self,
        company_id: str,
        username: str,
        metrics: list,
        calendar_year: int,
        investment_year: int,
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
            if investment_year is not None:
                return self.get_dynamic_investment_year_report(
                    company_id,
                    investment_year,
                    username,
                    from_main,
                    metrics,
                    access,
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
