def remove_white_spaces(string: str):
    from re import sub

    return sub(r"[\s]+", " ", string).strip()


def get_list_param(param: str) -> list:
    if param and param.strip() and len(param.strip()) > 1:
        return param.split(",")
    return []


def get_company_attr() -> dict:
    return {
        "sector": "sector",
        "vertical": "vertical",
        "investor_profile": "inves_profile_name",
        "growth_profile": "margin_group",
        "size": "size_cohort",
    }


def get_condition_params(query_params: dict) -> dict:
    condition_params = dict()
    if not query_params:
        return condition_params

    attr = get_company_attr()

    for key in query_params:
        if key in attr:
            param = attr[key]
            condition_params[param] = get_list_param(query_params[key])

    return condition_params
