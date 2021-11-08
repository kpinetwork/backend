class ResponseSQL:
    def __init__(self) -> None:
        pass

    def process_query_results(self, records) -> dict:
        response = []
        for row in records:
            response.append(dict(row))
        if len(response) == 0:
            return dict()
        return response[0]
