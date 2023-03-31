# Data Processing
This section describes how to execute python code to process data.

<br/>

***
## Dataset: Politicians Tweet Data (2022 and 2023)
***

### Raw files
- [US House Tweets from 2022 to 2023
](samples/us_politicians_twitter_2023/us_house_posts_2022_2023.csv)
- [US Senate Tweets from 2022 to 2023](samples/us_politicians_twitter_2023/us_senate_posts_2022_2023.csv)


### Process raw files
Execute the following code which will convert the raw files (listed above) into JSON files that are required by BigQuery for ingestion
```sh
cd fake-news-bears/samples
./02_twitter_politicians.py
```

Sample output is shown:
```
Senate file encoding is: utf_8
House file encoding is: utf_8
processDataFrame: shape is (139393, 11)
writeDataFrame: shape is (139393, 9), output file is: us_politicians_twitter_2023/02_us_senate_posts_for_bquery_2023.json
D:\fake-news-bears\samples\02_twitter_politicians.py:99: DtypeWarning: Columns (2) have mixed types. Specify dtype option on import or set low_memory=False.
  df_house = pd.read_csv(CSV_FILE_HOUSE)
processDataFrame: shape is (416812, 11)
writeDataFrame: shape is (412888, 9), output file is: us_politicians_twitter_2023/02_us_house_posts_for_bquery_2023.json
```

### Output
The following files are created as output:
- samples/us_politicians_twitter_2023/02_us_house_posts_for_bquery_2023.json
- samples/us_politicians_twitter_2023/02_us_senate_posts_for_bquery_2023.json
