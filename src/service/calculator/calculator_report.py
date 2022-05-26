class CalculatorReport:
    def __init__(
        self, logger, calculator, profile_range, company_anonymization
    ) -> None:
        self.logger = logger
        self.calculator = calculator
        self.profile_range = profile_range
        self.company_anonymization = company_anonymization

    def replace_revenue(self, company: dict) -> None:
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

    def get_rule_of_40(self, company: dict, company_revenue: int) -> dict:
        no_data = "NA"
        return {
            "id": company["id"],
            "name": company["name"],
            "revenue_growth_rate": company.get("growth", no_data),
            "ebitda_margin": company.get("ebitda_margin", no_data),
            "revenue": self.calculator.calculate_base_metric(company_revenue),
        }

    def anonymized_company(self, company: dict, allowed_companies: list) -> None:
        if company.get("id") not in allowed_companies:
            self.replace_revenue(company)
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

    def filter_by_condition(self, companies: dict, key: str, values: list) -> dict:
        if not values:
            return companies
        return {id: companies[id] for id in companies if companies[id][key] in values}

    def filter_by_conditions(self, data: dict, **conditions) -> dict:
        companies_filtered = dict()
        size_cohort = conditions.get("size_cohort", [])
        margin_group = conditions.get("margin_group", [])

        if len(size_cohort) == 0 and len(margin_group) == 0:
            return data

        companies_filtered = self.filter_by_condition(data, "size_cohort", size_cohort)
        companies_filtered = self.filter_by_condition(
            companies_filtered, "margin_group", margin_group
        )

        return companies_filtered

    def get_allowed_companies(self) -> list:
        return self.company_anonymization.companies

    def set_company_permissions(self, username: str) -> None:
        self.company_anonymization.set_company_permissions(username)
