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

    def process_rule_of_40_chart_results(self, records: list) -> list:
        result = self.process_query_list_results(records)

        values = filter(
            lambda elem: elem.get("revenue_growth_rate") is not None
            and elem.get("ebitda_margin") is not None
            and elem.get("revenue") is not None,
            result,
        )
        return list(values)

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

        def format_growth(peer_data: dict):
            if peer_data.get("growth"):
                peer_data["growth"] -= 100

        def calculate_rule_of_40(peer_data: dict):
            if peer_data.get("rule_of_40") is not None:
                revenue = peer_data.get("growth", 0)
                ebitda = peer_data.get("ebitda_margin", 0)
                peer_data["rule_of_40"] = (revenue - 100) + ebitda

            format_growth(peer_data)

        data = defaultdict(dict)

        [data[metric.get("id")].update(metric) for metric in records]
        [calculate_rule_of_40(peer) for company_id, peer in data.items()]

        return data
