import json


def load_config() -> dict:
    with open('config.json', 'r') as f:
        return json.load(f)