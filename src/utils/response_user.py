class ResponseUser:
    def __init__(self) -> None:
        pass

    def get_role_name(self, group) -> str:
        if not group:
            return ""
        role = group.split("_")
        return role[1] if role and len(role) == 3 else group

    def process_user_info(self, user, username) -> dict:
        if not user:
            return dict()
        status = "Active" if user.get("Enabled", True) else "Inactive"
        user_info = {
            "id": user.get("Username"),
            "email": username,
            "status": status,
            "created_at": user.get("UserCreateDate"),
        }
        return user_info

    def process_role_results(self, groups) -> list:
        if not groups:
            return []
        roles = [
            {
                "name": self.get_role_name(group.get("GroupName")),
                "description": group.get("Description"),
            }
            for group in groups
            if group.get("GroupName", "").find("Google") == -1
        ]
        return roles

    def process_user_roles(self, groups) -> list:
        if not groups or not groups.get("Groups"):
            return []
        return [
            self.get_role_name(group.get("GroupName"))
            for group in groups.get("Groups")
            if "google" not in group.get("GroupName", "").lower()
        ]
