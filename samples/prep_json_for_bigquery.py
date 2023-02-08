import json

# load file as JSON object for cleanup
json_obj = None
with open("samples/json_users_out/clean_twitter_user_profiles.json", "r") as infile:
    json_obj = json.load(infile)

print(f"type json object: {type(json_obj)}")

print(f"json keys: {json_obj.keys()}")

value = json_obj["top"]

print(f"type top value: {type(value)}")
print(f"top list first element type: {type(value[0])}")

top_dict01 = value[0]
print(f"top_dict01 keys: {top_dict01.keys()}")
