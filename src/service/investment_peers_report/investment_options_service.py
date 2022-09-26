from num2words import num2words


class InvestmentOptionsService:
    def __init__(self, session, query_builder, logger, response_sql) -> None:
        self.table_name = "investment"
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.logger = logger
        self.base_names = {
            0: "Year of investment",
            1: "full year after investment",
            -1: "years before investment",
        }

    def get_investment_years(self) -> list:
        try:
            invest = "investment_date"
            columns = [
                f"DISTINCT ON ({invest}) extract(year from {invest})::int as invest_year"
            ]
            query = (
                self.query_builder.add_table_name(self.table_name)
                .add_select_conditions(columns)
                .build()
                .get_query()
            )
            records = self.session.execute(query).fetchall()
            return self.response_sql.process_query_list_results(records)
        except Exception as error:
            self.logger.info(error)
            return []

    def get_metric_years(self) -> list:
        try:
            columns = [
                "DISTINCT ON(start_at) extract(year from start_at)::int as metric_year"
            ]
            query = (
                self.query_builder.add_table_name("time_period")
                .add_select_conditions(columns)
                .build()
                .get_query()
            )
            records = self.session.execute(query).fetchall()
            return self.response_sql.process_query_list_results(records)
        except Exception as error:
            self.logger.info(error)
            return []

    def get_years_from_list_of_dict(self, key: str, values: dict) -> list:
        return [value[key] for value in values]

    def get_years(self) -> list:
        invest_years = self.get_years_from_list_of_dict(
            "invest_year", self.get_investment_years()
        )
        if not invest_years:
            return []

        metric_years = self.get_years_from_list_of_dict(
            "metric_year", self.get_metric_years()
        )
        options = set()
        for invest_year in invest_years:
            for metric_year in metric_years:
                options.add(metric_year - invest_year)

        return sorted(list(options))

    def get_ordinal_year(self, year: int) -> str:
        year_name = num2words(year, ordinal=True).capitalize()
        return f"{year_name} {self.base_names[1]}"

    def get_cardinal_year(self, year: int) -> str:
        year = abs(year)
        if year == 1:
            return "Year before investment"
        year_name = num2words(year).capitalize()
        return f"{year_name} {self.base_names[-1]}"

    def get_year_name_function(self, key: int):
        options = {1: self.get_ordinal_year, -1: self.get_cardinal_year}
        return options[key]

    def get_year_name_option(self, year: int) -> str:
        if year == 0:
            return self.base_names[year]
        get_year_name = self.get_year_name_function(int(year / abs(year)))
        return get_year_name(year)

    def get_years_options(self) -> list:
        years = self.get_years()
        options = []

        for year in years:
            name = self.get_year_name_option(year)
            options.append({"value": year, "name": name})

        return options
