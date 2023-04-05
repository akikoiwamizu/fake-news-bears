# Data Processing
This section describes how to execute python code to process data.

<br/>


***
## Dataset: Politicians Last 100 Tweets from Twitter APIs
***
### Raw files
The raw files are:
- [Twitter Profiles CSV](json_users_out/20230205-143622_users_.json) links to the file `json_users_out/20230205-143622_users_.json`
- [Tweets Directory](json_users_out/) links to directory `json_users_out`

The directory `json_users_out` contains a large number of files that contain tweets from politicians. There are approximately `50,000` tweets.


***
### Process Raw User Profiles
***
The raw file `json_users_out/20230205-143622_users_.json` has twitter user profiles that require cleansing. The file is populated with double back slashes `\\` before quotes `"`, sometimes after quotes, etc. There are multiple bad character sequences that must be fixed.

Run [clean_twitter_user_profiles.py](clean_twitter_user_profiles.py) to cleanses the file:
```sh
# detox the data file and convert to strict JSON
./clean_twitter_user_profiles.py
```

The command above reads the CSV file, processes it, and creates an intermediary file: `json_users_out/clean_twitter_user_profiles.json`
This intermediary file is strictly JSON compliant and hence can be opened with python's JSON package.

However this file is *not* BigQuery friendly. It must be further processed with [prep_user_profile_json_for_bigquery.py](prep_user_profile_json_for_bigquery.py):
```sh
# convert strict JSON file to BigQuery compliant JSON
./prep_user_profile_json_for_bigquery.py
```

### Output
Output file is: `json_users_out/usa_congress_twitter_users.json`

This file can be uploaded to BigQuery. Sample from the file:
```json
{"created_at": "2014-12-11T19:54:07.000Z", "url": "https://t.co/ahR1R4P9AQ", "id": "2916086925", "verified": true, "public_metrics": {"followers_count": 29233, "following_count": 2611, "tweet_count": 13344, "listed_count": 923}, "username": "RepAdams", "name": "Rep. Alma Adams", "description": "Dean of NC Dems representing NC\\u2019s 12th District. Educator. Artist. Founder & Co-Chair of the Black Maternal Health @BMHCaucus and the Bipartisan @HBCUCaucus.", "verified_type": "government", "location": "Charlotte, NC", "protected": false, "profile_image_url": "https://pbs.twimg.com/profile_images/1532047017907724290/BNI4kV5T_normal.jpg", "entities": {"url": {"urls": [{"start": 0, "end": 23, "url": "https://t.co/ahR1R4P9AQ", "expanded_url": "http://adams.house.gov/", "display_url": "adams.house.gov"}]}, "description": {"mentions": [{"start": 115, "end": 125, "username": "BMHCaucus"}, {"start": 145, "end": 156, "username": "HBCUCaucus"}]}}}
```

***
### Process Raw Tweets
***
The directory `json_users_out` ([link](json_users_out/)) contains `521` CSV files that contain raw tweets.

All files are populated with double back slashes `\\` before quotes `"`, sometimes after quotes, etc. There are multiple bad character sequences that must be cleaned.

Sample from one file:
```txt
"{\"data\": [{\"created_at\": \"2023-02-05T20:39:11.000Z\", \"lang\": \"en\", \"context_annotations\": [{\"domain\": {\"id\": \"10\", \"name\": \"Person\",
```

Run [clean_twitter_user_tweets.py](clean_twitter_user_tweets.py) to cleanse the files:
```sh
# detox the data file and convert to strict JSON
./clean_twitter_user_tweets.py
```

Command output looks like:
```
D:\repo\fake-news-bears>python d:/repo/fake-news-bears/samples/clean_twitter_user_tweets.py
encoding is: ascii
Current dir: D:\repo\fake-news-bears
Source dir:  D:\repo\fake-news-bears/samples/json_tweets_out
Output dir:  D:\repo\fake-news-bears/samples/json_clean_tweets
File name: 20230205-142915_tweets_user_1002630999052865536.json
File Count: 521
batches: 1, stragglers: 22, total files: 522
processing batch# 0
Opened file: D:\repo\fake-news-bears/samples/json_tweets_out/20230205-142915_tweets_user_1002630999052865536.json
Opened file: D:\repo\fake-news-bears/samples/json_tweets_out/20230205-142915_tweets_user_1004891731.json
```


The command creates:
- directory `json_clean_tweets`
- file in the directory named `usa_congress_tweets.json`

### Output
Output file is: `json_tweets_out/usa_congress_tweets.json`
The file `usa_congress_tweets.json` contains JSON which is BigQuery compatible. I.e. it can be ingested by BigQuery without any issues.


