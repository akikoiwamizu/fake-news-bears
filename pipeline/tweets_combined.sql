create table tweets_score_combined as 
SELECT
  h.user_id,
  h.tweet_id,
  h.`not-hate`,
  i.`non_irony`,
  o.`not_offensive`,
  s.`dense_model_score`,
  s.`lstm_score`
FROM
  `fake-news-bears.hot_off_the_press.tweets_score_hate` h
JOIN
  `fake-news-bears.hot_off_the_press.tweets_score_irony` i
ON
  h.user_id = i.user_id
  AND h.tweet_id = i.tweet_id
JOIN
  `fake-news-bears.hot_off_the_press.tweets_score_offensive` o
ON
  h.user_id = o.user_id
  AND h.tweet_id = o.tweet_id
JOIN
`fake-news-bears.hot_off_the_press.truthfulness_scores_politicians` s 
ON 
  h.user_id = s.user_id
  AND h.tweet_id = s.tweet_id