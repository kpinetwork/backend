class UserDetailsService:
    def __init__(self, logger, client, response_user, policy_manager) -> None:
        self.logger = logger
        self.client = client
        self.response_user = response_user
        self.policy_manager = policy_manager

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

    def add_company_permissions(self, username: str, companies: list) -> dict:
        rules = {
            company: self.policy_manager.add_policy(
                username,
                company,
                self.policy_manager.ActionType.READ,
                self.policy_manager.ObjectType.COMPANY,
            )
            for company in companies
        }
        return rules

    def remove_company_permissions(self, username: str, companies: list) -> dict:
        rules = {
            company: self.policy_manager.remove_policy(
                username,
                company,
                self.policy_manager.ActionType.READ,
                self.policy_manager.ObjectType.COMPANY,
            )
            for company in companies
        }
        return rules

    def assign_company_permissions(self, username: str, companies: dict) -> dict:
        if username and username.strip() and companies:
            add_permissions = list(filter(lambda id: companies[id], companies))
            add_permissions_result = self.add_company_permissions(
                username, add_permissions
            )

            remove_permissions = list(filter(lambda id: not companies[id], companies))
            remove_result = self.remove_company_permissions(
                username, remove_permissions
            )
            add_permissions_result.update(remove_result)
            return add_permissions_result

        raise Exception("No valid username or companies data")
