from collections import OrderedDict

from profile_range import ProfileRange
from by_metric_report import ByMetricReport
from calculator_service import CalculatorService
from company_anonymization import CompanyAnonymization
from metric_report_repository import MetricReportRepository
from investment_date_repository import InvestmentDateReportRepository
from base_metrics_config_name import METRICS_TO_ANONYMIZE


class InvestmentDateReport:
    def __init__(
        self,
        logger,
        calculator: CalculatorService,
        repository: InvestmentDateReportRepository,
        metric_repository: MetricReportRepository,
        metric_report: ByMetricReport,
        profile_range: ProfileRange,
        company_anonymization: CompanyAnonymization,
    ) -> None:
        self.ranges = []
        self.logger = logger
        self.repository = repository
        self.calculator = calculator
        self.profile_range = profile_range
        self.company_anonymization = company_anonymization
        self.metric_repository = metric_repository
        self.by_metric_report = metric_report
        self.headers = [
            "id",
            "name",
            "metric name",
            "Investment - 2",
            "Investment - 1",
            "Year of investment",
            "Investment + 1",
            "Investment + 2",
            "Investment +3",
        ]

    def get_valid_year_records(self, company: dict, years: list) -> dict:
        metric_years = [*company["metrics"]]
        included_years = set(metric_years).union(set(years))
        return {
            year: company["metrics"].get(year, "NA")
            for year in included_years
            if year in years
        }

    def get_by_metric_records(
        self, metric: str, years: list, companies: dict, **conditions
    ) -> list:
        companies_data = dict()
        filters = self.metric_repository.add_filters(**conditions)
        data = self.by_metric_report.get_records(metric, years, filters)

        profiles = self.by_metric_report.get_profiles(filters)

        for id in data:
            company = data[id]
            if (company["id"] in companies) and (
                self.by_metric_report.is_in_range(profiles.get(id), **conditions)
            ):
                metric_data = dict()
                metric_data["metric_name"] = metric
                metric_values = self.get_records_by_invest_year(company, companies)
                data[id]["metrics"] = metric_values
                metric_data.update(self.sort_metric_values(metric_values))
                data[id]["metrics"].update(metric_data)
                companies_data[id] = company

        return companies_data

    def get_records_by_invest_year(self, company: dict, companies_by_invest) -> dict:
        years = [companies_by_invest[company["id"]]]
        years = self.repository.get_years(years)
        metric_data = self.get_valid_year_records(company, years)

        return metric_data

    def join_company_metrics(
        self,
        metrics: list,
        years: list,
        companies_by_investment,
        **conditions,
    ) -> dict:
        companies = dict()
        for metric in metrics:
            data = self.get_by_metric_records(
                metric, years, companies_by_investment, **conditions
            )
            for id in data:
                metric_values = list()
                if id in companies:
                    metric_values = companies[id]["metrics"]
                metric_values.append(data[id]["metrics"])
                companies[id] = data[id]
                companies[id]["metrics"] = metric_values

        return companies

    def sort_metric_values(self, metric_values: dict) -> dict:
        metric = {int(k): v for k, v in metric_values.items()}
        return OrderedDict(sorted(metric.items()))

    def get_companies_data(self, metrics: list, **conditions) -> dict:
        companies_result = dict()
        investments = self.repository.get_investments()
        companies = investments.keys()
        invest_years = [
            investments[company_id]["invest_year"] for company_id in investments
        ]

        companies_and_invest = dict(zip(companies, invest_years))
        years = self.repository.get_years(invest_years)
        companies_result = self.join_company_metrics(
            metrics, years, companies_and_invest, **conditions
        )

        return companies_result

    def get_anonymized_metric_data(
        self, metric: str, company_data: dict, metric_ranges: list
    ) -> list:
        try:
            name_field = "metric_name"
            metric_data = list(
                filter(
                    lambda metric_data: metric_data.get(name_field) == metric,
                    company_data["metrics"],
                )
            )
            standard_name = self.by_metric_report.clear_metric_name(metric)
            metric_data = metric_data[0]
            if standard_name not in METRICS_TO_ANONYMIZE.values():
                return [metric_data]
            metric_data.pop(name_field, None)
            metric_anonymized = self.by_metric_report.anonymized_metric(
                metric_data, metric_ranges.get(standard_name, [])
            )
            metric_anonymized[name_field] = metric
            return [metric_anonymized]
        except Exception as error:
            self.logger.error(error)
            return []

    def anonymize_company_metrics(
        self, company_data: dict, metric_ranges: dict, metrics: list
    ):
        company_data["name"] = self.by_metric_report.anonymized_name(
            company_data.get("id")
        )
        metrics_data = []
        for metric in metrics:
            metrics_data.extend(
                self.get_anonymized_metric_data(metric, company_data, metric_ranges)
            )
        company_data["metrics"] = metrics_data

    def anonymize_companies_data(self, companies_data: dict, metrics: list) -> None:
        metric_ranges = {
            self.by_metric_report.clear_metric_name(
                metric
            ): self.profile_range.get_profile_ranges(
                self.by_metric_report.clear_metric_name(metric)
            )
            for metric in metrics
        }
        for company_id in companies_data:
            if company_id not in self.company_anonymization.companies:
                self.anonymize_company_metrics(
                    companies_data[company_id], metric_ranges, metrics
                )

    def __needs_to_anonymize_metrics(self, metrics: list) -> bool:
        return any(
            [
                self.by_metric_report.clear_metric_name(metric)
                in METRICS_TO_ANONYMIZE.values()
                for metric in metrics
            ]
        )

    def get_peers_by_investment_date_report(
        self,
        company_id: str,
        username: str,
        metrics: list,
        from_main: bool,
        access: bool,
        **conditions,
    ) -> dict:
        try:
            company = dict()
            is_valid_company = company_id and company_id.strip()
            self.company_anonymization.set_company_permissions(username)

            data = self.get_companies_data(metrics, **conditions)
            if not access and self.__needs_to_anonymize_metrics(metrics):
                self.anonymize_companies_data(data, metrics)

            if not from_main and is_valid_company:
                company = data.pop(company_id, dict())

            peers = self.by_metric_report.sort_peers(data)

            return {
                "headers": self.headers,
                "company_comparison_data": company,
                "peers_comparison_data": peers,
            }
        except Exception as error:
            self.logger.error(error)
            raise error
