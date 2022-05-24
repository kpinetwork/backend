import uuid


class InvestmentsService:
    def __init__(self, session, query_builder, logger, response_sql) -> None:
        self.table_name = "investment"
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.logger = logger

    def get_company_investments(self, company_id: str) -> list:
        try:
            if company_id and company_id.strip():
                date_format = "YYYY-MM"
                select_columns = [
                    "company_id",
                    f"to_char(investment_date, '{date_format}') as investment_date",
                    f"to_char(divestment_date, '{date_format}') as divestment_date",
                    "round",
                    "structure",
                    "ownership",
                    "investor_type",
                ]
                query = (
                    self.query_builder.add_table_name(self.table_name)
                    .add_select_conditions(select_columns)
                    .add_sql_where_equal_condition(
                        {f"{self.table_name}.company_id": f"'{company_id}'"}
                    )
                    .build()
                    .get_query()
                )
                result = self.session.execute(query).fetchall()
                self.session.commit()
                return self.response_sql.process_query_list_results(result)
            return []

        except Exception as error:
            self.logger.info(error)
            raise error

    def add_investment(self, company_id: str, investment: dict) -> dict:
        try:
            if company_id and company_id.strip():
                investment_id = str(uuid.uuid4())
                investment_query = """
                INSERT INTO {table_name}{columns}
                VALUES{values}
                """.format(
                    table_name=self.table_name,
                    columns=self.__get_investment_columns(investment.copy()),
                    values=self.__get_investment_values(
                        investment.copy(), investment_id, company_id
                    ),
                )

                query = investment_query

                if investment.get("investor"):
                    investor_query = self.__get_investor_query(
                        investment_id, investment.get("investor")
                    )
                    query = ";".join([investment_query, investor_query])

                self.session.execute(query)
                self.session.commit()
                return investment
            return dict()

        except Exception as error:
            self.logger.info(error)
            raise error

    def __get_investor_query(self, investment_id: str, investor: str) -> str:
        values = self.__valid_values([str(uuid.uuid4()), investment_id, investor])
        query = """
        INSERT INTO investor
        VALUES{values} ;
        """.format(
            values="(" + ",".join(values) + ")"
        )
        return query

    def __get_investment_columns(self, investment):
        columns = ["id", "company_id"]
        investment.pop("investor", None)

        if investment.pop("invest", None):
            columns.append("investment_date")
        if len(investment.keys()) > 0:
            columns.extend(investment.keys())
        return "(" + ",".join(columns) + ")"

    def __get_investment_values(self, investment, investment_id, company_id):
        values = [investment_id, company_id]
        investment.pop("investor", None)
        invest_date = investment.pop("invest", None)

        if invest_date:
            values.append(f"{invest_date}-01")
        if len(investment.values()) > 0:
            values.extend(investment.values())

        return "(" + ",".join(self.__valid_values(values)) + ")"

    def __valid_values(self, values):
        valid_values = []
        for value in values:
            if isinstance(value, str):
                valid_values.append(f"'{value}'")
            else:
                valid_values.append(str(value))
        return valid_values
