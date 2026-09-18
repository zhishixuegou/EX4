## Import the necessary modules
import json
import os

## Logic for loading and reading from a JSON file.
## The function must return only the items
def load_items(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["items"]


## Logic for getting only those items that are not yet claimed
## It should return only the items that are unclaimed
def get_unclaimed_items(items):
    unclaimed = []
    for one_item in items:
        # 给定json status字符串 "unclaimed" / "claimed"
        if one_item.get("status") == "unclaimed":
            unclaimed.append(one_item)
    return unclaimed


## Logic to save the result to a JSON file.
## The function should create the directory if it does not exist and save the result in a JSON format.
def save_result(result, filename):
    dir_path = os.path.dirname(filename)
    if dir_path != "" and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as out_f:
        json.dump(result, out_f, indent=2)
