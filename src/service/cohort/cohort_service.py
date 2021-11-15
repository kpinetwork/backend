class CohortService:
    def __init__(self, session, query_sql, logger, response_sql):
        self.session = session
        self.table_name = "cohort"
        self.query_sql = query_sql
        self.response_sql = response_sql
        self.logger = logger
        pass

    def get_cohort_scenarios(self, cohort_id: str, scenario_type: str, year: str, offset=0, max_count=20) -> dict:
        try:
            if cohort_id and cohort_id.strip():
                scenario_name = f"{scenario_type}-{year}"
                query = "SELECT " \
                        "financial_scenario.name as scenario_name," \
                        "financial_scenario.currency as scenario_currency," \
                        "financial_scenario." \
                        "type as scenario_type," \
                        "company.name as company_name," \
                        "metric.name as metric_name," \
                        "metric.value as metric_value," \
                        "metric.type as metric_type," \
                        "metric.data_type as metric_data_type," \
                        "metric.name as metric_name" \
                        "FROM cohort_company " \
                        "INNER JOIN financial_scenario ON financial_scenario.company_id =  cohort_company.company_id " \
                        "INNER JOIN scenario_metric ON scenario_metric.scenario_id =  financial_scenario.id " \
                        "INNER JOIN company ON company.id =  cohort_company.company_id " \
                        "INNER JOIN metric ON metric.id =  scenario_metric.metric_id " \
                        "WHERE cohort_id = '{cohort_id}' " \
                        "AND financial_scenario.type = '{scenario_type}' " \
                        "AND financial_scenario.name = '{scenario_name}'".format(cohort_id=cohort_id,
                                                                                 scenario_type=scenario_type,
                                                                                 scenario_name=scenario_name)
                result = self.session.execute(query)
                self.session.commit()
                return self.response_sql.process_query_list_results(result)
            return dict()

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_cohort_information_by_id(self, cohort_id: str) -> dict:
        try:
            if cohort_id and cohort_id.strip():
                query = "SELECT COUNT(company.id) as total_companies, " \
                        "array_agg(DISTINCT(company.vertical)) as companies_vertical, " \
                        "array_agg(DISTINCT(company.sector)) as companies_sector, " \
                        "array_agg(DISTINCT(company.margin_group)) as companies_margin_group," \
                        "cohort.id  as cohort_id, " \
                        "cohort.name as cohort_name, " \
                        "cohort.tag as cohort_tag " \
                        "FROM cohort_company " \
                        "INNER JOIN company ON cohort_company.company_id = company.id " \
                        "INNER JOIN cohort ON cohort_company.cohort_id = cohort.id " \
                        "WHERE cohort_company.cohort_id ='{cohort_id}'" \
                        "GROUP BY cohort.id".format(cohort_id=cohort_id)

                result = self.session.execute(query)
                self.session.commit()
                records = result.fetchall()
                return self.response_sql.process_query_results(records)
            return dict()

        except Exception as error:
            self.logger.info(error)
            raise error

    def get_cohorts(self, offset=0, max_count=20) -> list:
        try:
            query = "SELECT COUNT(company.id) as total_companies, " \
                    "array_agg(DISTINCT(company.vertical)) as companies_vertical, " \
                    "array_agg(DISTINCT(company.sector)) as companies_sector, " \
                    "array_agg(DISTINCT(company.margin_group)) as companies_margin_group," \
                    "cohort.id  as cohort_id, " \
                    "cohort.name as cohort_name, " \
                    "cohort.tag as cohort_tag " \
                    "FROM cohort_company " \
                    "INNER JOIN company ON cohort_company.company_id = company.id " \
                    "INNER JOIN cohort ON cohort_company.cohort_id = cohort.id GROUP BY cohort.id"

            result = self.session.execute(query)
            self.session.commit()
            return self.response_sql.process_query_list_results(result)

        except Exception as error:
            self.logger.info(error)
            raise error
