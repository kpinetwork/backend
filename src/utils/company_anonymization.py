class CompanyAnonymization:
    def __init__(self) -> None:
        pass

    def anonymize_company_name(self, company_id: str) -> str:
        prefix_name = company_id[0:4]
        return prefix_name + "-xxxx"

    def anonymize_companies_list(self, results: list, key: str) -> list:
        anonymized_companies_list = list(
            map(
                lambda x: {
                    **x,
                    "name": self.anonymize_company_name(x.get(key)),
                },
                results,
            )
        )
        return anonymized_companies_list

    def anonymize_company_description(self, result: dict, key: str) -> dict:
        return {
            **result,
            "name": self.anonymize_company_name(result.get(key)),
        }
