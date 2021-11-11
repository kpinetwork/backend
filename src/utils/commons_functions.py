def remove_white_spaces(string: str):
    from re import sub

    return sub(r"[\s]+", " ", string).strip()
