class UsersService:
    def __init__(self, logger, client) -> None:
        self.logger = logger
        self.client = client

    def get_users_params(self, userPoolId) -> dict:
        return {"UserPoolId": userPoolId, "AttributesToGet": ["email"]}

    def get_users(self, userPoolId) -> list:
        def process_users(users, userPoolId) -> list:
            mapped_users = [
                {"username": user["Username"], "email": user["Attributes"][0]["Value"]}
                for user in users
            ]

            for user in mapped_users:
                groups = self.client.admin_list_groups_for_user(
                    Username=user["username"], UserPoolId=userPoolId
                )
                filter_groups = [
                    group["GroupName"]
                    for group in groups["Groups"]
                    if "Google" not in group["GroupName"]
                ]
                user.update({"roles": filter_groups})
            return mapped_users

        users = []
        params = self.get_users_params(userPoolId)
        response = self.client.list_users(**params)
        users.extend(response["Users"])

        mapped_users = process_users(users, userPoolId)
        return mapped_users
