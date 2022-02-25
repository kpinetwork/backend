import re


class CompanyAnonymization:
    def __init__(self, user_details_service) -> None:
        self.user_details_service = user_details_service
        self.companies = []

    def set_company_permissions(self, username) -> list:
        permisisons = self.user_details_service.get_user_company_permissions(username)
        self.companies = [
            permission.get("id") for permission in permisisons if permission.get("id")
        ]

    def anonymize_company_name(self, company_id: str) -> str:
        prefix_name = company_id[0:4]
        return prefix_name + "-xxxx"

    def anonymize_companies_list(self, results: list, key: str) -> list:
        def check_permission(company):
            if company.get(key) in self.companies:
                return company
            return {
                **company,
                "name": self.anonymize_company_name(company.get(key)),
            }

        anonymized_companies_list = list(map(lambda x: check_permission(x), results))
        return anonymized_companies_list

    def anonymize_company_description(self, result: dict, key: str) -> dict:
        if result.get(key) in self.companies:
            return result
        return {
            **result,
            "name": self.anonymize_company_name(result.get(key)),
        }

    def hide_companies(self, results: list, key: str) -> list:
        hiden_companies = list(filter(lambda x: x.get(key) in self.companies, results))
        return hiden_companies

    def is_anonymized(self, companie_name: str):
        matched = re.match(r"[\w][\w][\w][\w]-[x][x][x][x]", companie_name)
        return bool(matched)
