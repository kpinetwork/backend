from profile_range import ProfileRange
from calculator_service import CalculatorService
from company_anonymization import CompanyAnonymization
from base_metrics_config_name import METRICS_TO_ANONYMIZE


class BaseMetricsReport:
    def __init__(
        self,
        logger,
        calculator: CalculatorService,
        profile_range: ProfileRange,
        company_anonymization: CompanyAnonymization,
    ) -> None:
        self.logger = logger
        self.calculator = calculator
        self.profile_range = profile_range
        self.company_anonymization = company_anonymization

    def filter_by_condition(self, companies: dict, key: str, values: list) -> dict:
        if not values:
            return companies
        return {id: companies[id] for id in companies if companies[id][key] in values}

    def filter_by_conditions(self, data: dict, **conditions) -> dict:
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

    def get_peers_sorted(self, data: dict) -> list:
        return sorted(
            list(data.values()),
            key=lambda x: (
                self.company_anonymization.is_anonymized(x.get("name", "")),
                x.get("name", "").lower(),
            ),
        )

    def get_profiles_ranges(self) -> dict:
        anonymizable_metrics = [
            metric for metric in METRICS_TO_ANONYMIZE.values() if metric != "headcount"
        ]
        return {
            metric: self.profile_range.get_profile_ranges(metric)
            for metric in anonymizable_metrics
        }

    def anonymize_name(self, company: dict) -> None:
        anonymized_name = self.company_anonymization.anonymize_company_name(
            company.get("id")
        )
        company["name"] = anonymized_name

    def get_rule_of_40(self, company: dict, company_revenue: int) -> dict:
        no_data = "NA"
        return {
            "id": company["id"],
            "name": company["name"],
            "revenue_growth_rate": company.get("growth", no_data),
            "ebitda_margin": company.get("ebitda_margin", no_data),
            "revenue": self.calculator.calculate_base_metric(company_revenue),
        }

    def calculate_metrics(self, company: dict, profile_ranges: dict) -> None:
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
        company["size_cohort"] = self.profile_range.get_range_from_value(
            actuals_revenue, ranges=profile_ranges.get("revenue", [])
        )

        growth = self.calculator.calculate_growth_rate(
            actuals_revenue, prior_actuals_revenue
        )
        company["margin_group"] = self.profile_range.get_range_from_value(
            growth, profile="growth", ranges=profile_ranges.get("growth", [])
        )
        company["gross_profit"] = self.calculator.calculate_gross_profit(
            revenue, company.get("actuals_cost_of_goods")
        )
        company["gross_margin"] = self.calculator.calculate_gross_margin(
            revenue, company.get("actuals_cost_of_goods")
        )
        company[
            "sales_and_marketing"
        ] = self.calculator.calculate_sales_and_marketing_of_revenue(
            revenue, company.get("actuals_sales_marketing")
        )
        company[
            "general_and_admin"
        ] = self.calculator.calculate_general_and_admin_of_revenue(
            revenue, company.get("actuals_general_admin")
        )
        company[
            "research_and_development"
        ] = self.calculator.calculate_research_and_development_of_revenue(
            revenue, company.get("actuals_research_development")
        )
        company["clv_cac_ratio"] = self.calculator.calculate_ratio(
            company.get("actuals_customer_lifetime_value"),
            company.get("actuals_customer_acquition_costs"),
            1,
        )
        company["cac_ratio"] = self.calculator.calculate_ratio(
            company.get("actuals_customer_acquition_costs"),
            company.get("actuals_customer_annual_value"),
            2,
        )
        company["opex_of_revenue"] = self.calculator.calculate_opex_of_revenue(
            company.get("actuals_sales_marketing"),
            company.get("actuals_research_development"),
            company.get("actuals_general_admin"),
            company.get("actuals_other_operating_expenses"),
            revenue,
        )
        company[
            "revenue_per_employee"
        ] = self.calculator.calculate_revenue_per_employee(
            company.get("actuals_run_rate_revenue"), company.get("actuals_headcount")
        )
        company["gross_retention"] = self.calculator.calculate_gross_retention(
            company.get("prior_actuals_run_rate_revenue"),
            company.get("actuals_losses_and_downgrades"),
        )
        company["net_retention"] = self.calculator.calculate_net_retention(
            company.get("prior_actuals_run_rate_revenue"),
            company.get("actuals_losses_and_downgrades"),
            company.get("actuals_upsells"),
        )
        company["new_bookings_growth"] = self.calculator.calculate_new_bookings_growth(
            company.get("actuals_new_bookings"),
            company.get("prior_actuals_new_bookings"),
        )
        company["debt_ebitda"] = self.calculator.calculate_debt_ebitda(
            company.get("actuals_long_term_debt"), actuals_ebitda
        )
