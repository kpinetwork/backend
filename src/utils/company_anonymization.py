import os
import boto3
import logging
from user_details_service import UserDetailsService
from policy_manager import PolicyManager
from response_user import ResponseUser
from connection import get_db_uri


class CompanyAnonymization:
    def __init__(self) -> None:
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.db_uri = get_db_uri()
        self.response_user = ResponseUser()
        self.policy_manager = PolicyManager()
        self.user_pool_id = os.environ.get("USER_POOL_ID")
        boto3.Session(
            aws_access_key_id=os.environ.get("ACCESS_KEY"),
            aws_secret_access_key=os.environ.get("SECRET_KEY"),
            region_name="us-west-2",
        )
        self.cognito = boto3.client("cognito-idp")
        self.user_service = UserDetailsService(
            self.logger, self.cognito, self.response_user, self.policy_manager
        )

    def verify_user_access(self, user_id: str):
        try:
            roles = self.user_service.get_user_roles(user_id, self.user_pool_id)
            if isinstance(roles, list):
                if "admin" in roles:
                    # hacer todo normal
                    pass
                if "customer" in roles:
                    print("pertenece a grupo customer")
                return roles
        except Exception:
            return None

    def anonymize_company_name(self, company_id: str) -> str:
        prefix_name = company_id[0:4]
        return prefix_name + "-xxxx"

    def anonymize_companies_list(self, results: dict, key: str) -> list:
        companies_list = results.get(key)
        anonymized_companies_list = list(
            map(
                lambda x: {
                    **x,
                    "name": self.anonymize_company_name(x.get("company_id")),
                },
                companies_list,
            )
        )
        return anonymized_companies_list

    def anonymize_company_description(self, results: dict, key: str) -> dict:
        company_description = results.get(key)
        return {
            **company_description,
            "name": self.anonymize_company_name(company_description.get("company_id")),
        }
