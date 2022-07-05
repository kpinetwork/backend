from app_names import COMPARISON_METRICS


class DynamicReport:
    def __init__(
        self,
        logger,
        metric_report,
        investment_report,
        calendar_report,
    ) -> None:
        self.logger = logger
        self.metric_report = metric_report
        self.investment_report = investment_report
        self.calendar_report = calendar_report

    def __is_by_year_report(
        self, metric: str, calendar_year: int, invest_year: int
    ) -> bool:
        return (calendar_year or (invest_year is not None)) and not metric

    def __get_by_year_report_header(self) -> list:
        return ["name", "sector", "vertical"] + COMPARISON_METRICS

    def __comparison_report(self, header, company, peers) -> dict:
        return {
            "header": header,
            "company_comparison_data": company,
            "peers_comparison_data": peers,
        }

    def __get_metric_report(self, metric, access, username, **conditions) -> tuple:
        self.investment_report.report.set_company_permissions(username)
        years = self.metric_report.repository.get_years()
        header = ["name"] + years
        data = self.metric_report.get_by_metric_records(
            metric, years, access, **conditions
        )

        return header, data

    def __get_investment_report(
        self, investment_year, access, username, **conditions
    ) -> list:
        self.investment_report.report.set_company_permissions(username)
        data = self.investment_report.repository.get_base_metrics(
            int(investment_year), **conditions
        )

        self.investment_report.add_calculated_metrics(data, access)
        data = self.investment_report.report.filter_by_conditions(data, **conditions)

        return data

    def __get_dynamic_metrics(
        self,
        metric: str,
        calendar_year: int,
        invest_year: int,
        access: bool,
        username,
        **conditions,
    ) -> dict:
        companies = dict()
        filters = self.metric_report.repository.add_company_filters(**conditions)
        self.metric_report.company_anonymization.set_company_permissions(username)
        years = [calendar_year] if calendar_year else []

        if invest_year is not None:
            investments = self.investment_report.repository.get_investments()
            companies_with_investments = investments.keys()
            invest_year_by_company = {
                company_id: investments.get(company_id)["invest_year"] + invest_year
                for company_id in companies_with_investments
            }
            years = set(invest_year_by_company.values())
            filters.update(
                {
                    "company.id": [
                        f"'{company}'" for company in companies_with_investments
                    ]
                }
            )

        data = self.metric_report.get_records(metric, years, filters)
        profiles, sizes = self.metric_report.get_profiles(filters)

        for id in data:
            company = data[id]
            if self.metric_report.is_in_range(profiles.get(id), **conditions):
                self.metric_report.verify_anonimization(
                    access,
                    metric,
                    company,
                    sizes,
                    self.metric_report.company_anonymization.companies,
                )
                year_metric = (
                    invest_year_by_company.get(id)
                    if invest_year is not None
                    else years[0]
                )
                metric_value = {
                    metric: value
                    for key, value in company.get("metrics").items()
                    if key == year_metric
                }

                company.pop("metrics")
                company.update(metric_value)
                companies[id] = company

        return companies

    def get_dynamic_report(
        self,
        company_id: str,
        username: str,
        metric: str,
        calendar_year: int,
        investment_year: int,
        from_main: bool,
        access: bool,
        **conditions,
    ) -> dict:
        try:
            company = dict()
            is_valid_company = company_id and company_id.strip()
            header = []
            data = []

            if self.__is_by_year_report(
                metric, calendar_year, investment_year
            ) and not (investment_year is not None):
                peers_comparison = self.calendar_report.get_peers_comparison(
                    company_id, username, calendar_year, from_main, access, **conditions
                )
                header = self.__get_by_year_report_header()

                return self.__comparison_report(
                    header,
                    peers_comparison.get("company_comparison_data"),
                    peers_comparison.get("peers_comparison_data"),
                )

            elif (
                self.__is_by_year_report(metric, calendar_year, investment_year)
                and not calendar_year
            ):
                header = self.__get_by_year_report_header()
                data = self.__get_investment_report(
                    investment_year, access, username, **conditions
                )

            elif metric and not calendar_year and investment_year is None:
                header, data = self.__get_metric_report(
                    metric, access, username, **conditions
                )

            elif calendar_year or (investment_year is not None) and metric:
                header = ["name", metric]
                data = self.__get_dynamic_metrics(
                    metric,
                    calendar_year,
                    investment_year,
                    access,
                    username,
                    **conditions,
                )

            if not from_main and is_valid_company:
                company = data.pop(company_id, dict())

            peers = self.metric_report.sort_peers(data)

            return self.__comparison_report(header, company, peers)
        except Exception as error:
            self.logger.info(error)
            raise error
