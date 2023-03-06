create table `fake-news-bears.hot_off_the_press.users_scores_combined` as 
SELECT
  h.user_id,
  h.not_hate,
  h.low_3_not_hate_tweets,
  i.`non_irony`,
  i.low_3_non_irony_tweets,
  o.`not_offensive`,
  o.`low_3_not_offensive_tweets`,
  s.`avg_lstm_score`,
  s.`low_3_lstm_tweets`,
  s.`avg_dense_model_score`,
  s.`low_3_dense_tweets`
FROM
  `fake-news-bears.hot_off_the_press.users_score_hate` h
JOIN
  `fake-news-bears.hot_off_the_press.users_score_irony` i
ON
  h.user_id = i.user_id
JOIN
  `fake-news-bears.hot_off_the_press.users_score_offensive` o
ON
  h.user_id = o.user_id
JOIN
`fake-news-bears.hot_off_the_press.users_score_truthfulness` s 
ON 
  h.user_id = s.user_id