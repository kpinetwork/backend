from calculator_service import CalculatorService
from profile_range import ProfileRange
from company_anonymization import CompanyAnonymization
from base_metrics_repository import BaseMetricsRepository
from app_names import MetricNames, TableNames


class CompanyReportvsPeersService:
    def __init__(
        self,
        logger,
        calculator: CalculatorService,
        repository: BaseMetricsRepository,
        profile_range: ProfileRange,
        company_anonymization: CompanyAnonymization,
    ) -> None:
        self.logger = logger
        self.calculator = calculator
        self.profile_range = profile_range
        self.company_anonymization = company_anonymization
        self.repository = repository

    def get_company_data(self, company_id, year: int) -> dict:
        filters = {f"{TableNames.COMPANY}.id": f"'{company_id}'"}
        metrics = [MetricNames.REVENUE, MetricNames.EBITDA]
        data = self.repository.get_actuals_values(year, filters, metrics)
        budget_values = self.repository.get_budget_values(
            year, [year, year + 1], filters, metrics
        )
        prior_values = self.repository.get_prior_year_revenue_values(year, filters)

        companies = set([*data]).union(set([*budget_values]))

        for company_id in companies:
            data[company_id].update(budget_values.get(company_id, dict()))
            data[company_id].update(prior_values.get(company_id, dict()))

        return data

    def get_profiles(self, company: dict) -> dict:
        actuals_revenue = company.get("actuals_revenue")
        prior_revenue = company.get("prior_actuals_revenue")

        growth = self.calculator.calculate_growth_rate(actuals_revenue, prior_revenue)
        revenue = self.calculator.calculate_base_metric(actuals_revenue)
        size_range = self.profile_range.get_range_from_value(revenue, "size profile")
        growth_range = self.profile_range.get_range_from_value(growth, "growth profile")
        return {"size_cohort": size_range, "margin_group": growth_range}

    def get_description(self, company: dict) -> dict:
        params = ["id", "name", "sector", "vertical", "inves_profile_name"]
        description = dict()

        if not company:
            return description

        description = {param: company.get(param) for param in params}

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

            data = self.get_company_data(company_id, year)

            company = data.get(company_id, dict())

            return {
                "description": self.get_description(company),
                "financial_profile": self.get_financial_profile(company),
            }
        except Exception as error:
            self.logger.info(error)
            raise error
