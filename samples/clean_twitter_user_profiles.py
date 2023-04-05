# removes all the backslash (\) characters behind quotes
# loads the output as JSON
# removes the first data element
# serializes the JSON into a utf-8 text json file

# there are some unicode letters within the ascii such as \u2026
import re
from charset_normalizer import CharsetNormalizerMatches as CnM

encoding = (
    CnM.from_path("samples/json_users_out/20230205-143622_users_.json").best().first().encoding
)
print(f"encoding is: {encoding}")


# open the raw input file and create a new file that does not contain badly escaped data
# such as backslashed quotes e.g. replace \" with just "
with open("samples/json_users_out/20230205-143622_users_.json", "r") as infile, open(
    "samples/json_users_out/clean_twitter_user_profiles.json", "w"
) as outfile:
    print(f"file opened: {infile}")

    for line in infile:
        # replace all instances of \" with instances of "
        line = re.sub(r'(\\")', '"', line)

        # replaces instance of \\"KC\\" with \"KC\" or \\"some stuff here\\" with \"some stuff here\"
        line = re.sub(r'(\\\\")', '\\"', line)

        # remove the very first quote and the last quote in the file, i.e. "{ .... }" should be { .... } per JSON standards
        line = re.sub(r"^.|.$", "", line)

        # remove occurrences of two double quotes that are missing a comma
        # this happens because the file has top level elements combined
        # replace '...xyz}""{abc' with '...xyz},{abc'
        line = re.sub(r"(}\"\"{)", "},{", line)

        outfile.write(line)


print("file closed")

# ######
# open file at start and insert a top level array
line_index = 0
lines = None

# read file contents
with open("samples/json_users_out/clean_twitter_user_profiles.json", "r") as infile:
    lines = infile.readlines()

lines.insert(line_index, '{"top": [')

# write file contents
with open("samples/json_users_out/clean_twitter_user_profiles.json", "w") as writefile:
    writefile.writelines(lines)

# ######
# open file at end and close the top level array
with open("samples/json_users_out/clean_twitter_user_profiles.json", "a") as outfile:
    outfile.write("]}")
