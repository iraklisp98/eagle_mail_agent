import json
import os


def load_config(path="config.json"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"config.json not found at: {os.path.abspath(path)}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
