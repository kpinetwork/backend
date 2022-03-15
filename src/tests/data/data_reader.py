import json
import os


def read(file_name):
    root_path = os.path.abspath(".")
    with open(f"{root_path}/src/tests/data/{file_name}") as json_file:
        data = json.load(json_file)
        return data
