from collections import defaultdict


class ByMetricReport:
    def __init__(
        self,
        logger,
        calculator,
        repository,
        profile_range,
        company_anonymization,
    ) -> None:
        self.ranges = []
        self.logger = logger
        self.repository = repository
        self.calculator = calculator
        self.profile_range = profile_range
        self.company_anonymization = company_anonymization

    def get_standard_metrics(self) -> list:
        return [*self.repository.get_functions_metric(dict())]

    def get_base_metrics(self) -> list:
        return ["actuals_revenue", "actuals_ebitda", "budget_revenue", "budget_ebitda"]

    def get_dynamic_ranges(self, records: list) -> list:
        values = [record["value"] for record in records]
        return self.profile_range.build_ranges_from_values(values)

    def get_growth_metrics(self, company: dict, years: list) -> dict:
        metrics = dict()
        for year in years:
            actual = company["metrics"].get(year)
            prior = company["metrics"].get(year - 1)
            metrics[year] = self.calculator.calculate_growth_rate(actual, prior)
        return metrics

    def get_rule_of_40_metrics(
        self, growth_metrics: dict, margin_metrics: dict
    ) -> dict:
        metrics = dict()
        for year in growth_metrics:
            growth = growth_metrics.get(year)
            ebitda_margin = margin_metrics.get(year)

            rule_of_40 = self.calculator.calculate_sum(growth, ebitda_margin)
            metrics[year] = rule_of_40
        return metrics

    def calculate_base_metric(self, value: float, rounded: bool = True):
        metric_value = self.calculator.calculate_base_metric(value)
        return metric_value if rounded else value

    def process_standard_metrics(self, records: list, rounded: bool = True) -> dict:
        data = defaultdict(dict)
        self.ranges = self.get_dynamic_ranges(records)

        for record in records:
            company_id = record["id"]
            value = self.calculate_base_metric(record["value"], rounded)
            year_data = {record["year"]: value}
            company = {"id": record["id"], "name": record["name"], "metrics": year_data}
            if data.get(company_id):
                data[company_id]["metrics"].update(year_data)
            else:
                data[company_id] = company
        return data

    def process_growth(self, records: list, years: list) -> dict:
        data = defaultdict(dict)
        growth = self.process_standard_metrics(records, False)
        for id in growth:
            company = growth[id]
            metrics = self.get_growth_metrics(company, years)
            company = {"id": company["id"], "name": company["name"], "metrics": metrics}
            data[id] = company
        return data

    def process_rule_of_40(self, data_growth: dict, data_margin: dict) -> dict:
        companies = set([*data_growth] + [*data_margin])
        default_metrics = {"metrics": {}}
        data_rule = dict()
        for id in companies:
            margin_metrics = data_margin.get(id, default_metrics)["metrics"]
            growth_metrics = data_growth.get(id, default_metrics)["metrics"]
            metrics = self.get_rule_of_40_metrics(growth_metrics, margin_metrics)
            name = (
                data_margin.get(id).get("name")
                if data_margin.get(id)
                else data_growth[id].get("name")
            )
            data_rule[id] = {"id": id, "name": name, "metrics": metrics}
        return data_rule

    def get_revenues_values(self, revenues: list) -> dict:
        data = defaultdict(list)
        for record in revenues:
            scenario = [{"scenario": record["name"], "value": record["value"]}]
            data[record["id"]].extend(scenario)
        return data

    def get_profiles(self, filters: dict) -> tuple:
        revenues = self.get_revenues_values(
            self.repository.get_most_recents_revenue(filters)
        )
        sizes = self.profile_range.get_profile_ranges("size profile")
        growths = self.profile_range.get_profile_ranges("growth profile")

        data = defaultdict(dict)
        for company in revenues:
            revenues[company].extend([{}, {}])
            actuals, prior = tuple(
                [record.get("value") for record in revenues[company][:2]]
            )
            data[company] = {
                "size_cohort": self.profile_range.get_range_from_value(
                    actuals, ranges=sizes
                ),
                "margin_group": self.profile_range.get_range_from_value(
                    self.calculator.calculate_growth_rate(actuals, prior, False),
                    ranges=growths,
                ),
            }
        return (data, sizes)

    def get_no_standard_records(self, metric: str, years: list, filters: dict) -> dict:
        revenue = self.repository.get_metric_records("actuals_revenue", filters)
        data_growth = self.process_growth(revenue, years)
        if metric == "growth":
            return data_growth
        margin = self.repository.get_metric_records("ebitda_margin", filters)
        data_margin = self.process_standard_metrics(margin)
        return self.process_rule_of_40(data_growth, data_margin)

    def get_records(self, metric: str, years: list, filters: dict) -> dict:
        standard = self.get_standard_metrics()
        if metric in standard:
            records = self.repository.get_metric_records(metric, filters)
            return self.process_standard_metrics(records)
        return self.get_no_standard_records(metric, years, filters)

    def get_na_year_records(self, company: dict, years: list) -> dict:
        metric_years = [*company["metrics"]]
        not_included_years = set(metric_years) ^ set(years)
        return {year: "NA" for year in not_included_years}

    def is_in_range(self, profile: dict, **conditions) -> bool:
        size_cohort = conditions.get("size_cohort", [])
        margin_group = conditions.get("margin_group", [])
        contained = []
        if not profile:
            return False
        if size_cohort:
            contained.append(profile["size_cohort"] in size_cohort)
        if margin_group:
            contained.append(profile["margin_group"] in margin_group)

        return all(contained)

    def anonymized_name(self, id: str) -> str:
        return self.company_anonymization.anonymize_company_name(id)

    def anonymized_value(self, metric: str, metrics: dict, sizes: list) -> dict:
        _ranges = sizes if "revenue" in metric else self.ranges
        if metric not in self.get_base_metrics():
            return metrics

        return {
            year: self.profile_range.get_range_from_value(metrics[year], ranges=_ranges)
            for year in metrics
        }

    def verify_anonimization(
        self,
        access: bool,
        metric: str,
        company: dict,
        sizes: list,
        allowed_companies: list,
    ) -> None:
        if not access and company.get("id") not in allowed_companies:
            company["name"] = self.anonymized_name(company.get("id"))
            company["metrics"] = self.anonymized_value(
                metric, company["metrics"], sizes
            )

    def get_by_metric_records(
        self, metric: str, years: list, access: bool, **conditions
    ) -> dict:
        companies = dict()
        filters = self.repository.add_company_filters(**conditions)
        data = self.get_records(metric, years, filters)

        profiles, sizes = self.get_profiles(filters)

        for id in data:
            company = data[id]
            if self.is_in_range(profiles.get(id), **conditions):
                self.verify_anonimization(
                    access, metric, company, sizes, self.company_anonymization.companies
                )
                data[id]["metrics"].update(self.get_na_year_records(company, years))
                companies[id] = company

        return companies

    def sort_peers(self, data: dict) -> list:
        return sorted(
            list(data.values()),
            key=lambda x: (
                self.company_anonymization.is_anonymized(x.get("name", "")),
                x.get("name", "").lower(),
            ),
        )

    def get_by_metric_peers(
        self,
        company_id: str,
        username: str,
        metric: str,
        from_main: bool,
        access: bool,
        **conditions
    ) -> dict:
        try:
            company = dict()
            is_valid_company = company_id and company_id.strip()
            self.company_anonymization.set_company_permissions(username)
            years = self.repository.get_years()
            data = self.get_by_metric_records(metric, years, access, **conditions)

            if not from_main and is_valid_company:
                company = data.pop(company_id, dict())

            peers = self.sort_peers(data)

            return {
                "years": years,
                "company_comparison_data": company,
                "peers_comparison_data": peers,
            }
        except Exception as error:
            self.logger.info(error)
            raise error
