import os
import json


def write_to_json(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(content, f)


def read_from_file(path):
    if not os.path.isfile(path):
        return None

    with open(path, 'r') as f:
        return json.load(f)
