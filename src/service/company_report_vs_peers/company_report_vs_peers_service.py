class CompanyReportvsPeersService:
    def __init__(
        self, logger, calculator, repository, profile_range, company_anonymization
    ) -> None:
        self.logger = logger
        self.calculator = calculator
        self.repository = repository
        self.profile_range = profile_range
        self.company_anonymization = company_anonymization

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

    def get_profiles(self, company: dict) -> dict:
        actuals_revenue, prior_revenue = tuple(
            self.get_most_recent_revenues_value(company)
        )

        growth = self.calculator.calculate_growth_rate(actuals_revenue, prior_revenue)
        revenue = self.calculator.calculate_base_metric(actuals_revenue)
        size_range = self.get_metric_range(revenue, "size profile")
        growth_range = self.get_metric_range(growth, "growth profile")
        return {"size_cohort": size_range, "margin_group": growth_range}

    def get_most_recent_revenues_value(self, company: dict) -> list:
        company_id = company.get("id")
        result = self.repository.get_most_recents_revenue(company_id)
        result.extend([{}, {}])
        revenues = result[:2]
        return [revenue.get("value", "NA") for revenue in revenues]

    def get_description(self, company: dict) -> dict:
        params = ["id", "name", "sector", "vertical", "inves_profile_name"]
        description = dict()

        if not company:
            return description

        for param in params:
            description[param] = company.get(param)

        profiles = self.get_profiles(company)
        description.update(profiles)
        return description

    def get_financial_profile(self, company: dict) -> dict:
        financial_profile = dict()
        if not company:
            return financial_profile

        actuals_revenue = company.get("actuals_revenue")
        actuals_ebitda = company.get("actuals_ebitda")
        prior_revenue = company.get("prior_actuals_revenue")

        annual_rule_of_40 = self.calculator.calculate_rule_of_40(
            actuals_revenue, prior_revenue, actuals_ebitda
        )
        forward_budgeted_revenue_growth = self.calculator.calculate_growth_rate(
            company.get("next_budget_revenue"),
            company.get("budget_revenue"),
        )
        forward_budgeted_ebitda_growth = self.calculator.calculate_growth_rate(
            company.get("next_budget_ebitda"),
            company.get("budget_ebitda"),
        )
        forward_budgeted_rule_of_40 = self.calculator.calculate_rule_of_40(
            company.get("next_budget_revenue"),
            company.get("budget_revenue"),
            company.get("next_budget_ebitda"),
        )

        financial_profile = {
            "annual_revenue": self.calculator.calculate_base_metric(actuals_revenue),
            "annual_ebitda": self.calculator.calculate_base_metric(actuals_ebitda),
            "annual_rule_of_40": annual_rule_of_40,
            "forward_revenue_growth": forward_budgeted_revenue_growth,
            "forward_ebitda_growth": forward_budgeted_ebitda_growth,
            "forward_rule_of_40": forward_budgeted_rule_of_40,
        }
        return financial_profile

    def has_permissions(self, company_id: str) -> bool:
        allowed_companies = self.company_anonymization.companies
        return company_id in allowed_companies

    def get_company_report(
        self, company_id: str, username: str, year: int, access: bool
    ) -> dict:
        try:
            self.company_anonymization.set_company_permissions(username)
            user_has_permissions = (
                self.has_permissions(company_id) if not access else access
            )
            if not user_has_permissions:
                return dict()

            data = self.repository.get_base_metrics(
                year=year,
                need_all=True,
                company_id=company_id,
                need_actuals_prior_year=True,
                need_next_year=True,
            )

            company = data.get(company_id, dict())
            if not company:
                company = self.repository.get_company_description(company_id)

            return {
                "description": self.get_description(company),
                "financial_profile": self.get_financial_profile(company),
            }
        except Exception as error:
            self.logger.info(error)
            raise error
