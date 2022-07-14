class ComparisonvsPeersService:
    def __init__(self, logger, report, repository) -> None:
        self.logger = logger
        self.report = report
        self.repository = repository

    def remove_base_metrics(self, company: dict) -> None:
        base_metrics = [
            "actuals_revenue",
            "actuals_ebitda",
            "prior_actuals_revenue",
            "budget_revenue",
            "budget_ebitda",
            "actuals_cost_of_goods",
            "actuals_sales_of_marketing",
            "actuals_general_and_admin",
            "actuals_research_and_development",
        ]

        for metric in base_metrics:
            company.pop(metric, None)

    def get_comparison_vs_data(self, data: dict, access: bool) -> list:
        allowed_companies = self.report.get_allowed_companies()
        rule_of_40 = []

        for id in data:
            company_data = data[id]
            company_revenue = company_data.get("actuals_revenue")
            self.report.calculate_metrics(company_data)
            if not access and id not in allowed_companies:
                self.report.anonymized_company(company_data, allowed_companies)
            company_rule_of_40 = self.report.get_rule_of_40(
                company_data, company_revenue
            )
            if "NA" not in company_rule_of_40.values():
                rule_of_40.append(company_rule_of_40)
            self.remove_base_metrics(company_data)

        return rule_of_40

    def get_peers_comparison(
        self,
        company_id: str,
        username: str,
        year: str,
        from_main: bool,
        access: bool,
        **conditions
    ) -> dict:
        try:
            company = dict()
            is_valid_company = company_id and company_id.strip()
            self.report.set_company_permissions(username)
            data = self.repository.get_base_metrics(
                year=year,
                need_all=True,
                company_id=company_id,
                need_actuals_prior_year=True,
                need_next_year=False,
                **conditions
            )

            rule_of_40 = self.get_comparison_vs_data(data, access)

            data = self.report.filter_by_conditions(data, **conditions)

            if not from_main and is_valid_company:
                company = data.pop(company_id, dict())

            peers = self.report.get_peers_sorted(data)

            return {
                "company_comparison_data": company,
                "peers_comparison_data": peers,
                "rule_of_40": rule_of_40,
            }
        except Exception as error:
            self.logger.info(error)
            raise error
