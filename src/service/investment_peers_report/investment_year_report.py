class InvestmentYearReport:
    def __init__(self, logger, report, repository):
        self.logger = logger
        self.report = report
        self.repository = repository

    def get_unused_fields(self) -> list:
        scenarios = ["actuals", "budget"]
        metrics = [
            "revenue",
            "ebitda",
            "cost_of_goods",
            "sales_marketing",
            "general_admin",
            "research_development",
        ]
        fields = []
        for scenario in scenarios:
            for metric in metrics:
                name = f"{scenario}_{metric}"
                fields.extend([name, f"prior_{name}"])

        return fields

    def remove_unused_fields(self, company: dict) -> None:
        unused_fields = ["is_public", "scenario", "type", "value", "metric"]
        unused_fields.extend(self.get_unused_fields())

        for fields in unused_fields:
            company.pop(fields, None)

    def add_calculated_metrics(self, companies: dict, access: bool) -> None:
        allowed_companies = self.report.get_allowed_companies()

        for id in companies:
            company_data = companies[id]
            self.report.calculate_metrics(company_data)
            self.remove_unused_fields(company_data)
            if not access and id not in allowed_companies:
                self.report.anonymize_name(company_data)

        self.report.anonymized_companies_metrics(access, companies, allowed_companies)

    def get_peers_by_investment_year(
        self,
        company_id: str,
        invest_year: int,
        username: str,
        from_main: bool,
        access: bool,
        **conditions,
    ) -> dict:
        try:
            company = dict()
            is_valid_company = company_id and company_id.strip()
            self.report.set_company_permissions(username)
            data = self.repository.get_base_metrics(invest_year, **conditions)

            self.add_calculated_metrics(data, access)

            data = self.report.filter_by_conditions(data, **conditions)

            if not from_main and is_valid_company:
                company = data.pop(company_id, dict())

            peers = self.report.get_peers_sorted(data)

            return {
                "company_comparison_data": company,
                "peers_comparison_data": peers,
            }
        except Exception as error:
            self.logger.info(error)
            raise error
