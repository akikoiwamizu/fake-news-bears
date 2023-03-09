create table `hot_off_the_press.tweets_score_combined` as 
SELECT
  h.`user_id`,
  h.`tweet_id`,
  h.`not_hate`,
  i.`non_irony`,
  o.`not_offensive`,
  s.`dense_model_score`,
  s.`lstm_score`
FROM
  `fake-news-bears.hot_off_the_press.tweets_hate` h
JOIN
  `fake-news-bears.hot_off_the_press.tweets_irony` i
ON
  h.user_id = i.user_id
  AND h.tweet_id = i.tweet_id
JOIN
  `fake-news-bears.hot_off_the_press.tweets_offensive` o
ON
  h.user_id = o.user_id
  AND h.tweet_id = o.tweet_id

JOIN
`fake-news-bears.hot_off_the_press.truthfulness_scores_politicians` s 
ON 
  h.user_id = cast(s.author_id AS string)
  AND h.tweet_id = cast(s.tweet_id AS string)