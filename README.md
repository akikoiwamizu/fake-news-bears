# Fake News Bears

#### Team Members
* Akiko Iwamizu
* Brook Bi
* Giorgio Soggiu
* Jason Yang
* Razal Minhas
* Rohin Chabra


## The Problem
Media disinformation has the power to negatively impact countless lives and is often used to marginalize at-risk members of the population. It can spread like wildfire and the detection of fake news is often not simple. Our goal is to spread awareness and increase education by creating easy-to-understand scoring mechanisms for influential Twitter users' content.

## The Mission
**Fake News Bears** is focused on educating individuals about their exposure to and engagement with disinformation online which affects social media users worldwide. Using historical tweets from US politicians’ Twitter accounts, we apply existing disinformation detection and contextual models to calculate an aggregate score evaluating a politician’s Twitter account. For our MVP, we provide custom educational information on why that politician received a given score and the top three tweets that contributed to it.

[Visit our website to learn more.](https://www.fakenewsbears.org/)

## The Solution
The goal of our product is to educate social media users on US politicians' impact on the spread of disinformation on Twitter through an individualized, interactive, and informative platform experience. Our product features three main steps including tweet collection, model application, and custom reporting. Users can access our team's [Tableau Public dashboard](https://public.tableau.com/app/profile/brook.bi6046/viz/ModelScoreExploration-PoliticiansMVP/RadarDashboard) to view and compare any US Congress member's Twitter profile and learn more about the content they share online.


## Data Sources
Our product's dataset contains approximately 500,000 tweets published between 2022-2023 from 485 US Congress members. To collect the latest 100 tweets per politician, we created pipelines to extract this data using the Twitter API, and for historical tweet data, we used our partner Torch’s platform to extract tweets in CSV files. The politicians’ metadata including their Twitter handle, party affiliation, political office, and state/district was pulled from secondary sources including Press Gallery House and UC San Diego.

* US politician metadata
    * Includes fields like Twitter username, political party, political office, etc.
* Twitter profile user data
    * Includes fields like Twitter user id, follower count, number of posts, account creation date, etc.
* Twitter tweet text data
    * Includes fields like Twitter user id, tweet id, tweet text, like count, retweet count, etc.

### Dataset: Politicians Tweet Data (2022 and 2023)

#### Raw files
- [US House Tweets from 2022 to 2023
](samples/us_politicians_twitter_2023/us_house_posts_2022_2023.csv)
- [US Senate Tweets from 2022 to 2023](samples/us_politicians_twitter_2023/us_senate_posts_2022_2023.csv)

#### Data Processing
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

#### Output
The following files are created as output:
- samples/us_politicians_twitter_2023/02_us_house_posts_for_bquery_2023.json
- samples/us_politicians_twitter_2023/02_us_senate_posts_for_bquery_2023.json
