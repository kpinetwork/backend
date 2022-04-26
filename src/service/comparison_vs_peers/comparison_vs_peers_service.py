class ComparisonvsPeersService:
    def __init__(
        self, logger, calculator, repository, profile_range, company_anonymization
    ) -> None:
        self.logger = logger
        self.calculator = calculator
        self.repository = repository
        self.profile_range = profile_range
        self.company_anonymization = company_anonymization

    def remove_revenue(self, company: dict) -> None:
        revenue = company.get("revenue")
        ranges = self.profile_range.get_profile_ranges("size profile")
        if not self.calculator.is_valid_number(revenue):
            company["revenue"] = "NA"
        else:
            revenue_ranges = list(
                filter(
                    lambda range: self.profile_range.verify_range(range, revenue),
                    ranges,
                )
            )
            profile_range = (
                revenue_ranges[0]
                if (len(revenue_ranges) == 1 and revenue_ranges[0])
                else {"label": "NA"}
            )
            company["revenue"] = profile_range.get("label")

    def remove_base_metrics(self, company: dict) -> None:
        base_metrics = [
            "actuals_revenue",
            "actuals_ebitda",
            "prior_actuals_revenue",
            "budget_revenue",
            "budget_ebitda",
        ]

        for metric in base_metrics:
            company.pop(metric, None)

    def get_metric_range(self, metric: float, profile_type: str) -> str:
        if not self.calculator.is_valid_number(metric):
            return "NA"
        try:
            ranges = self.profile_range.get_profile_ranges(profile_type)
            metric_ranges = list(
                filter(
                    lambda range: self.profile_range.verify_range(range, metric),
                    ranges,
                )
            )
            return metric_ranges[0].get("label")
        except Exception as error:
            self.logger.info(error)
            return "NA"

    def calculate_metrics(self, company: dict) -> None:
        actuals_revenue = company.get("actuals_revenue")
        actuals_ebitda = company.get("actuals_ebitda")
        prior_actuals_revenue = company.get("prior_actuals_revenue")

        company["revenue"] = self.calculator.calculate_base_metric(actuals_revenue)
        company["growth"] = self.calculator.calculate_growth_rate(
            actuals_revenue, prior_actuals_revenue
        )
        company["ebitda_margin"] = self.calculator.calculate_ebitda_margin(
            actuals_ebitda, actuals_revenue
        )
        company["revenue_vs_budget"] = self.calculator.calculate_actual_vs_budget(
            actuals_revenue, company.get("budget_revenue")
        )
        company["ebitda_vs_budget"] = self.calculator.calculate_actual_vs_budget(
            actuals_ebitda, company.get("budget_ebitda")
        )
        company["rule_of_40"] = self.calculator.calculate_rule_of_40(
            actuals_revenue, prior_actuals_revenue, actuals_ebitda
        )
        revenue = self.calculator.calculate_base_metric(actuals_revenue)
        size_range = self.get_metric_range(revenue, "size profile")
        company["size_cohort"] = size_range

        growth = self.calculator.calculate_growth_rate(
            actuals_revenue, prior_actuals_revenue
        )
        growth_range = self.get_metric_range(growth, "growth profile")
        company["margin_group"] = growth_range

    def anonymized_company(self, company: dict, allowed_companies: list) -> None:
        if company.get("id") not in allowed_companies:
            self.remove_revenue(company)
            anonymized_name = self.company_anonymization.anonymize_company_name(
                company.get("id")
            )
            company["name"] = anonymized_name

    def get_peers_sorted(self, data: dict) -> list:
        return sorted(
            list(data.values()),
            key=lambda x: (
                self.company_anonymization.is_anonymized(x.get("name", "")),
                x.get("name", "").lower(),
            ),
        )

    def get_rule_of_40(self, company: dict, company_revenue: int) -> dict:
        no_data = "NA"
        return {
            "id": company["id"],
            "name": company["name"],
            "revenue_growth_rate": company.get("growth", no_data),
            "ebitda_margin": company.get("ebitda_margin", no_data),
            "revenue": self.calculator.calculate_base_metric(company_revenue),
        }

    def get_comparison_vs_data(self, data: dict, access: bool) -> list:
        allowed_companies = self.company_anonymization.companies
        rule_of_40 = []

        for id in data:
            company_data = data[id]
            company_revenue = company_data.get("actuals_revenue")
            self.calculate_metrics(company_data)
            if not access and id not in allowed_companies:
                self.anonymized_company(company_data, allowed_companies)
            company_rule_of_40 = self.get_rule_of_40(company_data, company_revenue)
            if "NA" not in company_rule_of_40.values():
                rule_of_40.append(company_rule_of_40)
            self.remove_base_metrics(company_data)

        return rule_of_40

    def filter_by_conditions(self, data: dict, **conditions) -> dict:
        companies_filtered = dict()
        size_cohort = conditions.get("size_cohort", [])
        margin_group = conditions.get("margin_group", [])

        if len(size_cohort) > 0 and len(margin_group) > 0:
            for company in data:
                if data[company]["size_cohort"] in conditions.get(
                    "size_cohort", []
                ) and data[company]["margin_group"] in conditions.get(
                    "margin_group", []
                ):
                    companies_filtered[company] = data[company]
        elif len(size_cohort) > 0 and len(margin_group) == 0:
            for company in data:
                if data[company]["size_cohort"] in conditions.get("size_cohort", []):
                    companies_filtered[company] = data[company]
        elif len(size_cohort) == 0 and len(margin_group) > 0:
            for company in data:
                if data[company]["margin_group"] in conditions.get("margin_group", []):
                    companies_filtered[company] = data[company]
        else:
            companies_filtered = data
        return companies_filtered

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
            self.company_anonymization.set_company_permissions(username)
            data = self.repository.get_base_metrics(
                year=year,
                need_all=True,
                company_id=company_id,
                need_actuals_prior_year=True,
                need_next_year=False,
                **conditions
            )

            rule_of_40 = self.get_comparison_vs_data(data, access)

            data = self.filter_by_conditions(data, **conditions)

            if not from_main and is_valid_company:
                company = data.pop(company_id, dict())

            peers = self.get_peers_sorted(data)

            return {
                "company_comparison_data": company,
                "peers_comparison_data": peers,
                "rule_of_40": rule_of_40,
            }
        except Exception as error:
            self.logger.info(error)
            raise error
