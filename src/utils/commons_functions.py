def remove_white_spaces(string: str):
    from re import sub

    return sub(r"[\s]+", " ", string).strip()


def get_list_param(param: str) -> list:
    if param and param.strip() and len(param.strip()) > 1:
        return param.split(",")
    return []
