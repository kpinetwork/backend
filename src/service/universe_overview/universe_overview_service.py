from statistics import mean


class UniverseOverviewService:
    def __init__(self, logger, calculator, repository, profile_range) -> None:
        self.logger = logger
        self.calculator = calculator
        self.repository = repository
        self.profile_range = profile_range

    def get_metrics_by_year(self, year: str, **conditions) -> dict:
        return self.repository.get_base_metrics(
            year, False, None, True, True, True, **conditions
        )

    def add_actuals_metrics(
        self,
        actuals_ebitda: float,
        actuals_revenue: float,
        prior_revenue: float,
        company: dict,
    ) -> None:
        growth = self.calculator.calculate_growth_rate(
            actuals_revenue, prior_revenue, False
        )
        company["growth"] = growth
        company["ebitda_margin"] = self.calculator.calculate_ebitda_margin(
            actuals_ebitda, actuals_revenue, False
        )
        company["rule_of_40"] = self.calculator.calculate_rule_of_40(
            actuals_revenue, prior_revenue, actuals_ebitda, False
        )
        company["size_cohort"] = self.get_profile_range(actuals_revenue, "size profile")
        company["margin_group"] = self.get_profile_range(growth, "growth profile")

    def add_budget_metrics(
        self,
        budget_ebitda: float,
        budget_revenue: float,
        budget_prior_revenue: float,
        company: dict,
    ) -> None:
        company["budget_growth"] = self.calculator.calculate_growth_rate(
            budget_revenue, budget_prior_revenue, False
        )
        company["budget_ebitda_margin"] = self.calculator.calculate_ebitda_margin(
            budget_ebitda, budget_revenue, False
        )

    def add_actuals_vs_budget_metrics(
        self,
        actuals_revenue: float,
        actuals_ebitda: float,
        budget_revenue: float,
        budget_ebitda: float,
        company: dict,
    ) -> None:
        company["revenue_vs_budget"] = self.calculator.calculate_actual_vs_budget(
            actuals_revenue, budget_revenue, False
        )
        company["ebitda_vs_budget"] = self.calculator.calculate_ebitda_margin(
            actuals_ebitda, budget_ebitda, False
        )

    def get_profile_range(self, metric: float, profile: str) -> str:
        if not self.calculator.is_valid_number(metric):
            return "NA"
        try:
            ranges = self.profile_range.get_profile_ranges(profile)
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

    def add_calculated_metrics_to_companies(self, data: list) -> None:
        for company in data:
            actuals_ebitda = company.get("actuals_ebitda")
            actuals_revenue = company.get("actuals_revenue")
            prior_revenue = company.get("prior_actuals_revenue")
            budget_ebitda = company.get("budget_ebitda")
            budget_revenue = company.get("budget_revenue")
            budget_prior_revenue = company.get("prior_budget_revenue")

            self.add_actuals_metrics(
                actuals_ebitda, actuals_revenue, prior_revenue, company
            )
            self.add_budget_metrics(
                budget_ebitda, budget_revenue, budget_prior_revenue, company
            )
            self.add_actuals_vs_budget_metrics(
                actuals_revenue, actuals_ebitda, budget_revenue, budget_ebitda, company
            )

    def get_kpi_average(self, metric: str, data: list) -> float:
        try:
            average = mean(
                company.get(metric)
                for company in data
                if self.calculator.is_valid_number(company.get(metric))
            )
            return round(average, 2)
        except Exception as error:
            self.logger.info(error)
            return 0

    def get_kpi_averages(self, data: list) -> list:
        growth = self.get_kpi_average("growth", data)
        margin = self.get_kpi_average("ebitda_margin", data)
        rule_of_40 = self.get_kpi_average("rule_of_40", data)

        return [
            {"growth": growth},
            {"ebitda_margin": margin},
            {"rule_of_40": rule_of_40},
        ]

    def get_companies_by_size_cohort(self, data: list) -> dict:
        companies_by_size = dict()
        for company in data:
            size = company.get("size_cohort")
            valid_size = size and size != "NA"
            if valid_size and size not in companies_by_size:
                companies_by_size[size] = [company]
            elif valid_size and size in companies_by_size:
                companies_by_size[size].append(company)
        return companies_by_size

    def get_count_by_size(self, data: dict) -> list:
        return [
            {"size_cohort": size_cohort, "count": len(companies)}
            for size_cohort, companies in data.items()
        ]

    def get_metric_by_size(self, data: dict, metric: str, alias: str) -> dict:
        return {
            size_cohort: {
                "size_cohort": size_cohort,
                alias: self.get_kpi_average(metric, companies),
            }
            for size_cohort, companies in data.items()
        }

    def merge_metric_dicts(self, metric: dict, pair_metric: dict) -> None:
        for size, metrics in metric.items():
            metrics.update(pair_metric.get(size, dict()))

    def get_growth_and_margin_by_size(
        self, data: dict, projected: bool = False
    ) -> dict:
        scenario = "budget_" if projected else ""
        growth_by_size = self.get_metric_by_size(data, f"{scenario}growth", "growth")
        margin_by_size = self.get_metric_by_size(
            data, f"{scenario}ebitda_margin", "margin"
        )

        self.merge_metric_dicts(growth_by_size, margin_by_size)

        return growth_by_size

    def get_revenue_and_ebitda_by_size(self, data: dict) -> dict:
        revenue_vs_budget = self.get_metric_by_size(
            data, "revenue_vs_budget", "revenue"
        )
        ebitda_vs_budget = self.get_metric_by_size(data, "ebitda_vs_budget", "ebitda")

        self.merge_metric_dicts(revenue_vs_budget, ebitda_vs_budget)

        return revenue_vs_budget

    def filter_by_conditions(self, data: list, **conditions) -> list:
        size_cohort = conditions.get("size_cohort", [])
        margin_group = conditions.get("margin_group", [])

        if len(size_cohort) > 0 and len(margin_group) > 0:
            companies_filtered = filter(
                lambda company: (
                    company["size_cohort"] in conditions.get("size_cohort", [])
                    and company["margin_group"] in conditions.get("margin_group", [])
                ),
                data,
            )
        elif len(size_cohort) > 0 and len(margin_group) == 0:
            companies_filtered = filter(
                lambda company: (
                    company["size_cohort"] in conditions.get("size_cohort", [])
                ),
                data,
            )
        elif len(size_cohort) == 0 and len(margin_group) > 0:
            companies_filtered = filter(
                lambda company: (
                    company["margin_group"] in conditions.get("margin_group", [])
                ),
                data,
            )
        else:
            companies_filtered = data
        return list(companies_filtered)

    def get_universe_overview(self, year: int, **conditions):
        try:
            data = self.get_metrics_by_year(year, **conditions).values()

            self.add_calculated_metrics_to_companies(data)

            data = self.filter_by_conditions(data, **conditions)

            kpi_average = self.get_kpi_averages(data)

            companies_by_size = self.get_companies_by_size_cohort(data)

            count_by_size = self.get_count_by_size(companies_by_size)
            growth_and_margin = self.get_growth_and_margin_by_size(
                companies_by_size, False
            )
            expected_growth_and_margin = self.get_growth_and_margin_by_size(
                companies_by_size, True
            )
            revenue_and_ebitda = self.get_revenue_and_ebitda_by_size(companies_by_size)

            return {
                "kpi_average": kpi_average,
                "count_by_size": count_by_size,
                "growth_and_margin": growth_and_margin,
                "expected_growth_and_margin": expected_growth_and_margin,
                "revenue_and_ebitda": revenue_and_ebitda,
            }
        except Exception as error:
            self.logger.info(error)
            raise error
