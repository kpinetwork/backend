from itertools import groupby


class ResponseSQL:
    def __init__(self) -> None:
        pass

    def process_query_result(self, records: list) -> dict:
        if len(records) == 0:
            return dict()

        response = []
        for row in records:
            response.append(dict(row))
        return response[0]

    def process_query_list_results(self, records: list) -> list:
        response = []
        [response.append(dict(record)) for record in records]
        return response

    def process_query_average_result(self, records: list) -> dict:
        result = self.process_query_result(records)

        average = result.get("average")

        return result if average else dict()

    def process_metrics_group_by_size_cohort_results(self, records: list) -> list:
        def get_key(elem) -> str:
            return elem.get("size_cohort")

        data = dict()
        records.sort(key=get_key)

        for size_cohort, value in groupby(records, key=get_key):
            data[size_cohort] = list(value)
        return data

    def proccess_base_metrics_results(self, records: list) -> dict:
        from collections import defaultdict

        data = defaultdict(dict)
        [data[metric.get("id")].update(metric) for metric in records]

        return data

    def process_companies_data_with_financial_information(self, records: list) -> dict:
        response = {}
        for record in records:
            company = dict(record)
            if company.get("id") in response.keys():
                self.__add_scenario_in_company(
                    company, response[company.get("id")]["scenarios"]
                )
            else:
                self.__add_company_information(company, response)

        return response

    def __add_scenario_in_company(self, company: dict, scenarios: dict) -> None:
        scenario = company.get("scenario")
        metric = company.get("metric")
        if scenario in scenarios.keys():
            scenarios[scenario].append(company.get("metric"))
        else:
            scenarios[scenario] = [metric]

    def __add_company_information(self, company: dict, companies: dict) -> None:
        companies.update(
            {
                company.get("id"): {
                    "company_id": company.get("id"),
                    "company_name": company.get("name"),
                    "scenarios": {company.get("scenario"): [company.get("metric")]},
                }
            }
        )
