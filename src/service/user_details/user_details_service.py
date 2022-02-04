class UserDetailsService:
    def __init__(self, logger, client, response_user) -> None:
        self.logger = logger
        self.client = client
        self.response_user = response_user

    def get_user_roles(self, username, user_pool_id) -> list:
        groups = self.client.admin_list_groups_for_user(
            Username=username, UserPoolId=user_pool_id
        )
        roles = self.response_user.process_user_roles(groups)
        return roles

    def get_user(self, user_pool_id, username) -> dict:
        response = self.client.admin_get_user(
            UserPoolId=user_pool_id, Username=username
        )
        user_info = self.response_user.process_user_info(response, username)
        user_info["roles"] = self.get_user_roles(username, user_pool_id)
        return user_info

    def get_user_details(self, user_pool_id, username) -> dict:
        user_info = self.get_user(user_pool_id, username)
        return {"user": user_info, "permissions": []}
