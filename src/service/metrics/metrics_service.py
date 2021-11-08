class MetricsService:
    def __init__(self, session, query_sql, logger, response_sql):
        self.session = session
        self.table_name = "metric"
        self.query_sql = query_sql
        self.response_sql = response_sql
        self.logger = logger
        pass

    def get_metric_by_id(self, metric_id: str) -> dict:
        try:
            if metric_id and metric_id.strip():
                query = self.query_sql.get_select_by_id_query(
                    self.table_name, metric_id
                )

                result = self.session.execute(query)
                self.session.commit()
                records = result.fetchall()
                return self.response_sql.process_query_results(records)
            return dict()

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_metrics(self, offset=0, max_count=20) -> list:
        try:
            query = self.query_sql.get_select_query(self.table_name, offset, max_count)

            results = self.session.execute(query)
            self.session.commit()

            metrics = []
            [metrics.append(dict(record)) for record in results]
            return metrics

        except Exception as error:
            self.logger.info(error)
            raise error
