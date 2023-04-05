=======
# Fake News Bears

#### Authors
* Akiko Iwamizu
* Brook Bi
* Giorgio Soggiu
* Jason Yang
* Razal Minhas
* Rohin Chabra


## Overview

The goal of this UC Berkeley MIDS Capstone is to build tech to help educated social media users about their exposure to and engagement with disinformation online.

Our goal is to reduce the spread of disinformation, and to accomplish this, we score users based on a series of dimensions calculated from their Twitter content. We then provide the user their top three tweets that contributed to their disinformation score. What's unique about our approach is that we segment Twitter users at an individual-level and customize the education information users receive on our platform.

The MVP is built using US politician Twitter data, but we hope to connect with privacy experts and investors to take our product to the next level so we can provide these features to Twitter users worldwide.

[Visit our website to learn more.](https://www.fakenewsbears.org/)

=======
## Data Processing
This section describes how to execute python code to process data.

***
## Dataset: Politicians Last 100 Tweets from Twitter APIs
***

### Raw files
The raw files are:

### Process raw files
The following commands process the files

### Output
The files output are

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
cd fake-news-bears\samples
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