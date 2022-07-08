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

    def __get_dynamic_report_dict(
        self, header: list, company: dict, peers: list
    ) -> dict:
        return {
            "header": header,
            "company_comparison_data": company,
            "peers_comparison_data": peers,
        }

    def __is_by_year_report(
        self, metric: str, calendar_year: int, invest_year: int
    ) -> bool:
        return (calendar_year or (invest_year is not None)) and not metric

    def __get_by_year_report_header(self) -> list:
        base_header = ["name", "sector", "vertical"]
        base_header.extend(COMPARISON_METRICS)
        return base_header

    def __get_by_year_report(
        self,
        calendar_year: int,
        invest_year: int,
        company_id: str,
        username: str,
        from_main: bool,
        access: bool,
        **conditions,
    ) -> dict:
        if calendar_year is not None:
            return self.__get_calendar_year_report(
                company_id, calendar_year, username, from_main, access, **conditions
            )
        if invest_year is not None:
            return self.__get_invest_year_report(
                company_id, invest_year, username, from_main, access, **conditions
            )

    def __get_calendar_year_report(
        self,
        company_id: str,
        calendar_year: int,
        username: str,
        from_main: bool,
        access: bool,
        **conditions,
    ) -> dict:
        peers_comparison = self.calendar_report.get_peers_comparison(
            company_id, username, calendar_year, from_main, access, **conditions
        )
        header = self.__get_by_year_report_header()

        return self.__get_dynamic_report_dict(
            header,
            peers_comparison.get("company_comparison_data"),
            peers_comparison.get("peers_comparison_data"),
        )

    def __get_invest_year_report(
        self,
        company_id: str,
        invest_year: int,
        username: str,
        from_main: bool,
        access: bool,
        **conditions,
    ) -> list:
        header = self.__get_by_year_report_header()
        investment_report = self.investment_report.get_peers_by_investment_year(
            company_id, invest_year, username, from_main, access, **conditions
        )
        investment_report.update({"header": header})

        return investment_report

    def __get_metric_report(
        self, metric: str, access: bool, username: str, **conditions
    ) -> tuple:
        self.investment_report.report.set_company_permissions(username)
        years = self.metric_report.repository.get_years()
        header = ["name"] + years
        data = self.metric_report.get_by_metric_records(
            metric, years, access, **conditions
        )

        return header, data

    def __get_investment_values(self, invest_year: int) -> tuple:
        investments = self.investment_report.repository.get_investments()
        companies_with_investments = investments.keys()
        invest_year_by_company = {
            company_id: investments.get(company_id)["invest_year"] + invest_year
            for company_id in companies_with_investments
        }
        filters = {
            "company.id": [f"'{company}'" for company in companies_with_investments]
        }

        return invest_year_by_company, filters

    def __get_valid_metric_value(self, metric_dict: dict, metric: str) -> dict:
        if metric_dict:
            return metric_dict
        return {metric: "NA"}

    def __get_company_dict(
        self,
        id: str,
        company: str,
        invest_year_by_company: dict,
        invest_year: int,
        years: list,
        metric: str,
    ) -> dict:
        year_metric = (
            invest_year_by_company.get(id) if invest_year is not None else years[0]
        )
        metric_value = {
            metric: (value if value else "NA")
            for key, value in company.get("metrics").items()
            if key == year_metric
        }
        company.pop("metrics")
        company.update(self.__get_valid_metric_value(metric_value, metric))

        return company

    def __get_dynamic_metrics(
        self,
        metric: str,
        calendar_year: int,
        invest_year: int,
        access: bool,
        username: str,
        **conditions,
    ) -> dict:
        invest_year_by_company = dict()
        years = [calendar_year] if calendar_year else []
        filters = self.metric_report.repository.add_company_filters(**conditions)
        self.metric_report.company_anonymization.set_company_permissions(username)

        if invest_year is not None:
            invest_year_by_company, invest_filters = self.__get_investment_values(
                invest_year
            )
            years = set(invest_year_by_company.values())
            filters.update(invest_filters)

        data = self.metric_report.get_records(metric, years, filters)
        profiles, sizes = self.metric_report.get_profiles(filters)

        return self.__get_dynamic_dict(
            data,
            profiles,
            sizes,
            metric,
            invest_year_by_company,
            invest_year,
            years,
            access,
            **conditions,
        )

    def __get_dynamic_dict(
        self,
        data: list,
        profiles: dict,
        sizes: dict,
        metric: str,
        invest_year_by_company: dict,
        invest_year: int,
        years: list,
        access: bool,
        **conditions,
    ):
        companies = dict()
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
                company = self.__get_company_dict(
                    id, company, invest_year_by_company, invest_year, years, metric
                )
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
            data = dict()

            if self.__is_by_year_report(metric, calendar_year, investment_year):
                return self.__get_by_year_report(
                    calendar_year,
                    investment_year,
                    company_id,
                    username,
                    from_main,
                    access,
                    **conditions,
                )

            elif metric and calendar_year is None and investment_year is None:
                header, data = self.__get_metric_report(
                    metric, access, username, **conditions
                )

            elif calendar_year is not None or investment_year is not None and metric:
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

            return self.__get_dynamic_report_dict(header, company, peers)
        except Exception as error:
            self.logger.info(error)
            raise error
