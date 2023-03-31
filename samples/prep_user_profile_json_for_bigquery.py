import json

# strict JSON formatted file
INPUT_JSON = "samples/json_users_out/clean_twitter_user_profiles.json"

# BigQuery friendly JSON file
OUTPUT_JSON = "samples/json_users_out/usa_congress_twitter_users.json"

# load file as JSON object for cleanup
json_obj = None
with open(INPUT_JSON, "r") as infile:
    json_obj = json.load(infile)

print(f"type json object: {type(json_obj)}")

print(f"json keys: {json_obj.keys()}")

top_list = json_obj["top"]

print(f"type top value: {type(top_list)}")
print(f"top list size: {len(top_list)}")
print(f"top list first element type: {type(top_list[0])}")

final_list = []
# go through list of dict (data-error pairs) items
for i in range(0, len(top_list)):
    list_dict = top_list[i]
    print(f"top list[{i}] is dict, with keys: {list_dict.keys()}")

    # get the data from the dict
    data_list = list_dict["data"]

    # copy list under data into new item
    print(f"type of data_list is:{type(data_list)}")
    print(f"length of data_list is: {len(data_list)}")

    final_list.extend(data_list)

# save list to json file
print(f"final_list length: {len(final_list)}")
with open(OUTPUT_JSON, "w") as outfile:
    for i in range(0, len(final_list)):
        s = json.dumps(final_list[i])

        # write one line of json (without an ending comma)
        # this formats the data correctly for BigQuery ingestion
        outfile.write(s + "\n")
