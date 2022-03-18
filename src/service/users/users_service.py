class UsersService:
    def __init__(self, logger, client, response_user) -> None:
        self.logger = logger
        self.client = client
        self.response_user = response_user

    def get_users_params(self, user_pool_id) -> dict:
        return {"UserPoolId": user_pool_id, "AttributesToGet": ["email"]}

    def get_users(self, user_pool_id) -> list:
        def process_users(users, user_pool_id) -> list:
            mapped_users = [
                {"username": user["Username"], "email": user["Attributes"][0]["Value"]}
                for user in users
            ]

            for user in mapped_users:
                groups = self.client.admin_list_groups_for_user(
                    Username=user["username"], UserPoolId=user_pool_id
                )
                filter_groups = self.response_user.process_user_roles(groups)
                user.update({"roles": filter_groups})
            return mapped_users

        users = []
        params = self.get_users_params(user_pool_id)
        response = self.client.list_users(**params)
        users.extend(response["Users"])

        mapped_users = process_users(users, user_pool_id)
        return sorted(mapped_users, key=lambda user: user.get("email"))

    def get_roles_params(self, user_pool_id) -> dict:
        return {
            "UserPoolId": user_pool_id,
            "Limit": 4,
        }

    def get_roles(self, user_pool_id) -> list:
        params = self.get_roles_params(user_pool_id)
        result = self.client.list_groups(**params)
        _groups = result.get("Groups")
        groups = _groups if _groups else []
        roles = self.response_user.process_role_results(groups)
        return roles
