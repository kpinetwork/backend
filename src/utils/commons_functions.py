from app_names import TableNames


def remove_white_spaces(string: str):
    from re import sub

    return sub(r"[\s]+", " ", string).strip()


def get_list_param(param: str) -> list:
    if param and param.strip() and len(param.strip()) > 2:
        return param.split(",")
    return []


def get_conditions(query_params: dict, attributes: dict) -> dict:
    conditions = dict()
    if not query_params:
        return conditions

    for key in query_params:
        if key in attributes:
            param = attributes[key]
            conditions[param] = get_list_param(query_params[key])
    return conditions


def get_company_attr() -> dict:
    return {
        "investor_profile": f"{TableNames.COMPANY}.inves_profile_name",
        "growth_profile": "margin_group",
        "size": "size_cohort",
        "tag": f"{TableNames.TAG}.name",
    }


def get_condition_params(query_params: dict) -> dict:
    attrs = get_company_attr()
    return get_conditions(query_params, attrs)


def get_edit_modify_attr() -> dict:
    return {
        "names": "name",
        "sectors": "sector",
        "verticals": "vertical",
        "investor_profiles": "inves_profile_name",
        "scenarios": "scenarios",
    }


def get_edit_modify_condition_params(query_params: dict) -> dict:
    attrs = get_edit_modify_attr()
    return get_conditions(query_params, attrs)
