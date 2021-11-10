class MetricsService:
    def __init__(self, session, query_sql, logger, response_sql):
        self.session = session
        self.table_name = "metric"
        self.query_sql = query_sql
        self.response_sql = response_sql
        self.logger = logger
        pass

    def get_metric_by_company_id(self, company_id: str) -> dict:
        try:
            if company_id and company_id.strip():
                query = (
                    "SELECT "
                    "metric.id , metric.name , metric.value, metric.type , "
                    "metric.data_type,metric.period_id ,time_period.start_at,"
                    "time_period.end_at FROM {table_name} "
                    "INNER JOIN time_period ON time_period.id = metric.period_id "
                    "WHERE company_id='{company_id}' ORDER BY start_at DESC".format(
                        table_name=self.table_name, company_id=company_id
                    )
                )

                result = self.session.execute(query)
                self.session.commit()
                return self.response_sql.process_query_list_results(result)
            return dict()

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_metrics(self, offset=0, max_count=20) -> list:
        try:
            query = self.query_sql.get_select_query(self.table_name, offset, max_count)

            results = self.session.execute(query)
            self.session.commit()

            return self.response_sql.process_query_list_results(results)

        except Exception as error:
            self.logger.info(error)
            raise error
