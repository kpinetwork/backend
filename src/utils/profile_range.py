from strenum import StrEnum


class ProfileType(StrEnum):
    SIZE = "size profile"
    GROWTH = "growth profile"


class ProfileRange:
    def __init__(self, session, query_builder, logger, response_sql) -> None:
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.logger = logger
        self.table = "value_range"

    def get_profile_ranges(self, type: str) -> list:
        try:
            query = (
                self.query_builder.add_table_name(self.table)
                .add_select_conditions(["label, min_value, max_value"])
                .add_sql_where_equal_condition({f"{self.table}.type": f"'{type}'"})
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            self.session.commit()
            return self.response_sql.process_query_list_results(result)
        except Exception as error:
            self.logger.info(error)
            return []

    def verify_range(self, range, revenue):
        max_value = range.get("max_value")
        min_value = range.get("min_value")
        coincidences = []
        if max_value:
            coincidences.append(revenue < max_value)
        if min_value:
            coincidences.append(revenue >= min_value)
        return coincidences and all(coincidences)
