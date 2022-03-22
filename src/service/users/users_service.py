class UsersService:
    def __init__(self, logger, client, response_user) -> None:
        self.logger = logger
        self.client = client
        self.response_user = response_user

    def get_users_params(self, user_pool_id: str, limit: int, token: str) -> dict:
        params = {
            "UserPoolId": user_pool_id,
            "AttributesToGet": ["email"],
            "Limit": limit,
        }
        if token and token.strip():
            params["PaginationToken"] = token
        return params

    def get_roles_params(self, user_pool_id) -> dict:
        return {
            "UserPoolId": user_pool_id,
            "Limit": 4,
        }

    def set_users_groups(self, users, user_pool_id) -> list:
        for user in users:
            groups = self.client.admin_list_groups_for_user(
                Username=user.get("username"), UserPoolId=user_pool_id
            )
            filter_groups = self.response_user.process_user_roles(groups)
            user.update({"roles": filter_groups})

    def get_users(self, user_pool_id: str, limit: int = 10, token: str = None) -> list:
        params = self.get_users_params(user_pool_id, limit, token)
        response = self.client.list_users(**params)
        users = self.response_user.proccess_users(response.get("Users", []))

        self.set_users_groups(users, user_pool_id)
        sort = sorted(users, key=lambda user: user.get("email"))
        return {"users": sort, "token": response.get("PaginationToken")}

    def get_groups(self, user_pool_id):
        params = self.get_roles_params(user_pool_id)
        result = self.client.list_groups(**params)
        _groups = result.get("Groups")
        groups = _groups if _groups else []
        return groups

    def get_roles(self, user_pool_id) -> list:
        groups = self.get_groups(user_pool_id)
        roles = self.response_user.process_role_results(groups)
        return roles
