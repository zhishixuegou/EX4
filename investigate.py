## Import the necessary modules
import json
import os
import ollama

## Import the function from the module parse_data
from parse_data import load_items, get_unclaimed_items, save_result


## Build your prompt based on the description the user provides
## and the items that are available in the lost-and-found database.
## The model must follow the rules listed in the README file
## The function should return the system prompt and the user prompt.
## You may need to use json.dumps() to convert the available_items list into a JSON string.
def build_prompt(description, available_items):
    system_prompt = """
You are campus lost‑and‑found matching assistant. Follow ALL these rules strictly:
1. You MUST ONLY use the provided lost‑and‑found JSON item list as your source knowledge. Do NOT invent any items.
2. Item match does NOT require every detail to be identical; partial feature match is acceptable for possible candidates.
3. Important! Each database item uses these keys: "id", "item", "color", "location", "date", "status". The item unique identifier is "id".
4. Your output MUST BE ONLY a single valid JSON object. No extra text, no markdown, no explanation, no thinking notes.
5. Required JSON schema:
{
    "matches": ["ITEM_ID"],
    "confidence": "LOW"
}
    - "matches": list of item id strings (the value from key "id") for all possible matching items. If zero matches return empty list [].
    - "confidence": MUST be exactly one string value: "LOW", "MEDIUM", "HIGH". No other text allowed.
6. Do NOT add any keys outside "matches" and "confidence".
"""
    items_json_str = json.dumps(available_items, ensure_ascii=False)
    user_prompt = f"""
LOST‑AND‑FOUND DATABASE ITEMS:
{items_json_str}

USER LOST ITEM DESCRIPTION:
{description}

Find all possible matching item IDs (field "id"), produce only the required JSON output.
"""
    return system_prompt, user_prompt


## Logic to ask Qwen for all the possible matches based on the system prompt and user prompt.
## The function should return the response from Qwen.
def ask_qwen(system_prompt, user_prompt):
    response = ollama.chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response["message"]["content"]


## Logic to parse the response from Qwen and return the result.
## You may need to use json.loads() to convert the response string into a suitable Python data structure.
def parse_response(response_text):
    cleaned = response_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    result = json.loads(cleaned)
    return result


## Logic to validate the result returned by Qwen.
## It should check if the result is a dictionary, contains the keys "matches" and "confidence", and that the values are of the correct type.
## If everything is correct, then it should check if the item IDs in the "matches" list are valid IDs .
def validate_result(result, available_items):
    if not isinstance(result, dict):
        return False
    required_keys = {"matches", "confidence"}
    if not required_keys.issubset(result.keys()):
        return False
    matches = result["matches"]
    confidence = result["confidence"]
    if not isinstance(matches, list):
        return False
    if not isinstance(confidence, str):
        return False
    if confidence not in ("LOW", "MEDIUM", "HIGH"):
        return False
    # 真实id字段是 "id"
    valid_ids = {item["id"] for item in available_items}
    for item_id in matches:
        if item_id not in valid_ids:
            return False
    return True


## Logic to display the matches found by Qwen in a user‑friendly format.
def display_matches(result, available_items):
    print("""
CAMPUS LOST-AND-FOUND ASSISTANT
==================================================""")
    print("Searching for possible matches...")
    print("MATCH RESULT")
    print("-" * 50)
    print(f"Confidence: {result['confidence']}")
    print("Possible matches:")
    matches_list = result["matches"]
    if len(matches_list) == 0:
        print("    No matches found (empty list)")
    else:
        item_map = {item["id"]: item for item in available_items}
        for mid in matches_list:
            it = item_map[mid]
            print(f"ID: {mid}")
            print(f"Item: {it.get('item','')}")
            print(f"Color: {it.get('color','')}")
            print(f"Location: {it.get('location','')}")
            print(f"Date found: {it.get('date','')}")
    print("Result saved to output/match_result.json")


## Control center for the entire program.
def main():
    items = load_items("found_items.json")
    unclaimed_items = get_unclaimed_items(items)

    user_description = input("Describe the item you lost: ")

    sys_prompt, usr_prompt = build_prompt(user_description, unclaimed_items)

    raw_response_text = ask_qwen(sys_prompt, usr_prompt)

    parsed_result = parse_response(raw_response_text)

    is_valid = validate_result(parsed_result, unclaimed_items)
    if not is_valid:
        parsed_result = {
            "matches": [],
            "confidence": "LOW"
        }

    save_result(parsed_result, "output/match_result.json")

    display_matches(parsed_result, unclaimed_items)


if __name__ == "__main__":
    main()
