class CompanyService:
    def __init__(
        self, session, query_builder, logger, response_sql, company_anonymization
    ) -> None:
        self.table_name = "company"
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.logger = logger
        self.company_anonymization = company_anonymization

    def get_company(self, company_id: str) -> dict:
        try:
            if company_id and company_id.strip():
                query = (
                    self.query_builder.add_table_name(self.table_name)
                    .add_select_conditions(
                        [f"{self.table_name}.*", "company_location.city"]
                    )
                    .add_join_clause(
                        {
                            "company_location": {
                                "from": f"{self.table_name}.id",
                                "to": "company_location.company_id",
                            }
                        },
                        self.query_builder.JoinType.LEFT,
                    )
                    .add_sql_where_equal_condition(
                        {f"{self.table_name}.id": f"'{company_id}'"}
                    )
                    .build()
                    .get_query()
                )

                result = self.session.execute(query).fetchall()
                self.session.commit()

                return self.response_sql.process_query_result(result)
            return dict()

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_all_companies(self, offset=0, max_count=20) -> list:
        try:
            query = (
                self.query_builder.add_table_name(self.table_name)
                .add_select_conditions(
                    [f"{self.table_name}.*", "company_location.city"]
                )
                .add_join_clause(
                    {
                        "company_location": {
                            "from": f"{self.table_name}.id",
                            "to": "company_location.company_id",
                        }
                    },
                    self.query_builder.JoinType.LEFT,
                )
                .add_sql_order_by_condition(["name"], self.query_builder.Order.ASC)
                .add_sql_offset_condition(offset)
                .add_sql_limit_condition(max_count)
                .build()
                .get_query()
            )
            results = self.session.execute(query).fetchall()
            self.session.commit()
            return self.response_sql.process_query_list_results(results)

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_all_public_companies(self, offset=0, max_count=20, access=False) -> list:
        try:
            where_condition = {f"{self.table_name}.is_public": True}
            query = (
                self.query_builder.add_table_name(self.table_name)
                .add_select_conditions(
                    [f"{self.table_name}.*", "company_location.city"]
                )
                .add_join_clause(
                    {
                        "company_location": {
                            "from": f"{self.table_name}.id",
                            "to": "company_location.company_id",
                        }
                    },
                    self.query_builder.JoinType.LEFT,
                )
                .add_sql_where_equal_condition(where_condition)
                .add_sql_order_by_condition(["name"], self.query_builder.Order.ASC)
                .add_sql_offset_condition(offset)
                .add_sql_limit_condition(max_count)
                .build()
                .get_query()
            )
            results = self.session.execute(query).fetchall()
            self.session.commit()
            companies = self.response_sql.process_query_list_results(results)
            if access:
                return companies
            anonymized_companies = self.company_anonymization.hide_companies(
                companies, "id"
            )
            return sorted(
                anonymized_companies,
                key=lambda x: x.get("name", "").lower(),
            )
        except Exception as error:
            self.logger.info(error)
            raise error

    def change_company_publicly(self, companies_data) -> bool:
        try:
            query = (
                self.query_builder.add_table_name(self.table_name)
                .add_set_conditions({"is_public": "c.public_value"})
                .add_from_values_statement(
                    companies_data, "c(company_id, public_value)"
                )
                .add_sql_where_equal_condition(
                    {"c.company_id": f"{self.table_name}.id"}
                )
                .build_update()
                .get_query()
            )
            self.session.execute(query)
            self.session.commit()

            return True

        except Exception as error:
            self.logger.info(error)
            raise error
