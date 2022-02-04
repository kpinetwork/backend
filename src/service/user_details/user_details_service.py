class UserDetailsService:
    def __init__(self, logger, client, response_user) -> None:
        self.logger = logger
        self.client = client
        self.response_user = response_user

    def get_username_by_email(self, email, user_pool_id) -> str:
        users = self.client.list_users(
            UserPoolId=user_pool_id, Limit=1, Filter=f'email="{email}"'
        )
        _users = users.get("Users", [])
        user = _users[0] if _users else dict()
        return user.get("Username")

    def get_user_roles(self, username, user_pool_id) -> list:
        groups = self.client.admin_list_groups_for_user(
            Username=username, UserPoolId=user_pool_id
        )
        roles = self.response_user.process_user_roles(groups)
        return roles

    def get_user(self, user_pool_id, email) -> dict:
        username = self.get_username_by_email(email, user_pool_id)
        response = self.client.admin_get_user(
            UserPoolId=user_pool_id, Username=username
        )
        user_info = self.response_user.process_user_info(response, email)
        user_info["roles"] = self.get_user_roles(username, user_pool_id)
        return user_info

    def get_user_details(self, user_pool_id, username) -> dict:
        user_info = self.get_user(user_pool_id, username)
        return {"user": user_info, "permissions": []}
