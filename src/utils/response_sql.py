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

    def process_scenarios_list_results(self, records: list) -> list:
        result = self.process_query_list_results(records)
        data = dict()
        for record in result:
            company_id = record.get("company_id")
            if data.get(company_id):
                scenarios = data.get(company_id).get("scenarios")
                scenarios.append(record)

            else:
                data[company_id] = {"company": dict(), "scenarios": []}
                data[company_id]["company"] = {
                    "id": company_id,
                    "name": record.get("company_name"),
                }
                data[company_id]["scenarios"] = [record]

        return list(data.values())

    def process_metrics_group_by_size_cohort_results(self, records: list) -> list:
        def get_key(elem) -> str:
            return elem.get("size_cohort")

        data = dict()
        records.sort(key=get_key)

        for size_cohort, value in groupby(records, key=get_key):
            data[size_cohort] = list(value)
        return data

    def proccess_comparison_results(self, records: list) -> dict:
        from collections import defaultdict

        data = defaultdict(dict)

        [data[metric.get("id")].update(metric) for metric in records]
        return data
