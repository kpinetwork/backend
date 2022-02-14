import logging
import casbin
import casbin_sqlalchemy_adapter
from strenum import StrEnum
from connection import get_db_uri


class PolicyManager:
    def __init__(self) -> None:
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.db_uri = get_db_uri()
        self.adapter = casbin_sqlalchemy_adapter.Adapter(self.db_uri)

        casbin_sqlalchemy_adapter.CasbinRule
        self.e = casbin.Enforcer("./model.conf", self.adapter)

    class ObjectType(StrEnum):
        COMPANY = "Company"
        METRIC = "Metric"
        SCENARIO = "Scenario"

    class ActionType(StrEnum):
        READ = "read"
        WRITE = "write"
        DELETE = "delete"

    def verify_access(
        self, user_id: str, object_id: str, action: ActionType, type: ObjectType
    ) -> bool:
        return True if self.e.enforce(user_id, object_id, action, type) else False

    def add_policy(
        self, user_id: str, object_id: str, action: ActionType, type: ObjectType
    ) -> bool:
        return self.e.add_policy(user_id, object_id, action, type)

    def add_policies(self, rules: list[list]) -> bool:
        return self.e.add_policies(rules)

    def remove_policy(
        self, user_id: str, object_id: str, action: ActionType, type: ObjectType
    ) -> bool:
        return self.e.remove_policy(user_id, object_id, action, type)

    def remove_policies(self, rules: list[list]) -> bool:
        return self.e.remove_policies(rules)
