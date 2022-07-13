from app_names import TableNames


class MetricTypesService:
    def __init__(self, session, query_builder, response_sql, logger) -> None:
        self.logger = logger
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql

    def get_metric_types(self) -> list:
        try:
            query = (
                self.query_builder.add_table_name(TableNames.METRIC_TYPES)
                .build()
                .get_query()
            )

            results = self.session.execute(query)
            names = self.response_sql.process_query_list_results(results)
            return [name.get("name") for name in names if name.get("name")]
        except Exception as error:
            self.logger.info(error)
            return []
