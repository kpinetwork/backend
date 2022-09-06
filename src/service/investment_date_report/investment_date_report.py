from collections import OrderedDict
from by_metric_report import ByMetricReport
from calculator_service import CalculatorService
from company_anonymization import CompanyAnonymization
from investment_date_repository import InvestmentDateReportRepository
from metric_report_repository import MetricReportRepository
from profile_range import ProfileRange


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
        included_years = set(metric_years) & set(years)
        included_years = set(metric_years).union(set(years))
        return {
            year: company["metrics"].get(year, "NA")
            for year in included_years
            if year in years
        }

    def get_by_metric_records(
        self, metric: str, years: list, access: bool, companies: dict, **conditions
    ) -> list:
        companies_data = dict()
        filters = self.metric_repository.add_company_filters(**conditions)
        data = self.by_metric_report.get_records(metric, years, filters)

        profiles, sizes = self.by_metric_report.get_profiles(filters)

        for id in data:
            company = data[id]
            if (company["id"] in companies) and (
                self.by_metric_report.is_in_range(profiles.get(id), **conditions)
            ):
                metric_data = dict()
                metric_data["metric_name"] = metric
                self.by_metric_report.verify_anonimization(
                    access,
                    metric,
                    company,
                    sizes,
                    self.company_anonymization.companies,
                )
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
        access: bool,
        companies_by_investment,
        **conditions,
    ) -> dict:
        companies = dict()
        for metric in metrics:
            data = self.get_by_metric_records(
                metric, years, access, companies_by_investment, **conditions
            )
            company_data = dict()
            for id in data:
                metric_values = list()
                company_data = data[id]
                if id in companies:
                    metric_values = companies[id]["metrics"]
                metric_values.append(data[id]["metrics"])
                companies[id] = company_data
                companies[id]["metrics"] = metric_values

        return companies

    def sort_metric_values(self, metric_values: dict) -> dict:
        metric = {int(k): v for k, v in metric_values.items()}
        return OrderedDict(sorted(metric.items()))

    def get_companies(self, metrics: list, access: bool, **conditions) -> dict:
        companies_result = dict()
        investments = self.repository.get_investments()
        companies = investments.keys()
        initial_year = 0
        invest_years = [
            investments[company_id]["invest_year"] + initial_year
            for company_id in investments
        ]

        companies_and_invest = dict(zip(companies, invest_years))
        years = self.repository.get_years(invest_years)
        companies_result = self.join_company_metrics(
            metrics, years, access, companies_and_invest, **conditions
        )

        return companies_result

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

            data = self.get_companies(metrics, access, **conditions)

            if not from_main and is_valid_company:
                company = data.pop(company_id, dict())

            peers = self.by_metric_report.sort_peers(data)

            return {
                "headers": self.headers,
                "company_comparison_data": company,
                "peers_comparison_data": peers,
            }
        except Exception as error:
            self.logger.info(error)
            raise error
