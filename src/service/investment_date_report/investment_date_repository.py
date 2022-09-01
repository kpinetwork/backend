from collections import defaultdict


class InvestmentDateReportRepository:
    def __init__(self, session, query_builder, response_sql, logger):
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.logger = logger
        self.scenario_table_label = "scenario"

    def get_investments(self) -> dict:
        try:
            query = (
                self.query_builder.add_table_name("investment")
                .add_select_conditions(self.get_investments_columns())
                .add_sql_order_by_condition(
                    ["company_id", "investment_date", "round"],
                    self.query_builder.Order.ASC,
                )
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            self.session.commit()
            return self.get_investments_dict(
                self.response_sql.process_query_list_results(result)
            )
        except Exception as error:
            self.logger.info(error)
            return dict()

    def get_investments_dict(self, records: list) -> dict:
        investment_data = defaultdict(dict)
        [investment_data[invest.get("company_id")].update(invest) for invest in records]

        return investment_data

    def get_investments_columns(self) -> list:
        return [
            "DISTINCT ON(company_id) company_id",
            "extract(year from investment_date)::int as invest_year",
            "round",
        ]

    def get_years(self, years: list) -> list:
        metric_years = set()
        for year in years:
            metric_years.add(year + 3)
            metric_years.add(year + 2)
            metric_years.add(year + 1)
            metric_years.add(year)
            metric_years.add(year - 1)
            metric_years.add(year - 2)
        return list(metric_years)
