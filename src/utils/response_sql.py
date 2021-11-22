class ResponseSQL:
    def __init__(self) -> None:
        pass

    def process_query_result(self, records) -> dict:
        if len(records) == 0:
            return dict()

        response = []
        for row in records:
            response.append(dict(row))
        return response[0]

    def process_query_list_results(self, records) -> list:
        response = []
        [response.append(dict(record)) for record in records]
        return response
