from collections import OrderedDict


class InvestmentDateReport:
    def __init__(
        self,
        logger,
        calculator,
        repository,
        metric_repository,
        metric_report,
        profile_range,
        company_anonymization,
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

    def get_by_metric_records(
        self, metric: str, years: list, access: bool, company_id, **conditions
    ) -> list:
        metric_data = dict()
        company_data = dict()
        filters = self.metric_repository.add_company_filters(**conditions)
        data = self.by_metric_report.get_records(metric, years, filters)

        profiles, sizes = self.by_metric_report.get_profiles(filters)

        for id in data:
            company = data[id]
            if (company["id"] == company_id) and (
                self.by_metric_report.is_in_range(profiles.get(id), **conditions)
            ):
                metric_data["metric_name"] = metric
                self.by_metric_report.verify_anonimization(
                    access,
                    metric,
                    company,
                    sizes,
                    self.company_anonymization.companies,
                )
                data[id]["metrics"].update(
                    self.by_metric_report.get_na_year_records(company, years)
                )
                metric_data.update(self.sort_metric_values(data[id]["metrics"]))
                company_data["id"] = company["id"]
                company_data["name"] = company["name"]

        return [company_data, metric_data]

    def get_by_company_metrics(
        self, metrics: list, years: list, access: bool, company_id, **conditions
    ) -> dict:
        company = dict()
        metrics_values = list()
        for metric in metrics:
            data = self.get_by_metric_records(
                metric, years, access, company_id, **conditions
            )
            company.update(data[0])
            metrics_values.append(data[1])
        company["metrics"] = metrics_values
        return company

    def sort_metric_values(self, metric_values: dict) -> dict:
        metric = {int(k): v for k, v in metric_values.items()}
        return OrderedDict(sorted(metric.items()))

    def get_companies_metrics(self, metrics: list, access: bool, **conditions) -> dict:
        companies_result = dict()
        investments = self.repository.get_investments()
        companies = investments.keys()
        invest_year = 0

        for company in companies:
            years = [investments[company]["invest_year"] + invest_year]
            years = self.repository.get_years(years)
            companies_result[company] = self.get_by_company_metrics(
                metrics, years, access, company, **conditions
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

            data = self.get_companies_metrics(metrics, access, **conditions)

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
