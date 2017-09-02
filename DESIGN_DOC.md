## Design Doc
### What is this repo about?
This is a POC to use data from [Reddit Posts Data](https://bigquery.cloud.google.com/dataset/fh-bigquery:reddit_posts) to calculate:
* Subreddit Daily Leaderboard
> Reddit users ranked by number of posts submitted daily for each subreddit.
* Submission Streak
> Reddit users' day to day post submission streak.

### Data structure
Data are from [Reddit Posts Data](https://bigquery.cloud.google.com/dataset/fh-bigquery:reddit_posts), we will be using the following columns:
* created_utc - post created timestamp (in seconds)
* subreddit - subreddit name
* author - post author
* num_comments - number of comments on the post
* score - upvotes - downvotes on the post
(each row is one post)

### How does it work?
A CSV of the data from [Reddit Posts Data](https://bigquery.cloud.google.com/dataset/fh-bigquery:reddit_posts) 
is ingested using pandas, the leaderboard and submission streak is then calculated and saved to two CSVs 
(by running ```make_report_csv.py```), which can be viewed later (```leaderboard.html``` and ```streak.html```). [Intructions on how to run.](https://github.com/chunchuck2000/reddit_posts)

Calculations logic summarised in SQL (BigQuery dialect):
* Subreddit Leaderboard
``` SQL
SELECT
    *,
    RANK() OVER (PARTITION BY post_date, subreddit 
                 ORDER BY num_posts DESC, 
                          score DESC, 
                          num_comments DESC, 
                          author
                 ) AS daily_rank,
    COUNT(DISTINCT author) OVER (PARTITION BY post_date, subreddit) AS daily_total_rank,
  FROM
    (  
      SELECT
        DATE(SEC_TO_TIMESTAMP(created_utc)) AS post_date,
        subreddit,
        author,
        COUNT(*) AS num_posts,
        SUM(score) as score,
        SUM(num_comments) as num_comments
      FROM [reddit_posts]
      WHERE author <> '[deleted]' AND subreddit IS NOT NULL
      GROUP BY 1, 2, 3
    )
```

* Submission Streak
``` SQL
SELECT
  author,
  streak_group,
  MIN(post_date) as streak_start,
  COUNT(*) as streak_length,
  SUM(score) as score,
  SUM(num_comments) as num_comments,
  SUM(num_posts) as num_posts,
FROM (
  SELECT
    *,
    post_order - DATEDIFF(post_date, first_post_date) AS streak_group 
  FROM (
    SELECT
      *,
      RANK() OVER (PARTITION BY author ORDER BY post_date) AS post_order,
      MIN(post_date) OVER (PARTITION BY author) AS first_post_date
    FROM (
        SELECT
          DATE(SEC_TO_TIMESTAMP(created_utc)) AS post_date,
          author,
          COUNT(*) AS num_posts,
          SUM(score) AS score,
          SUM(num_comments) AS num_comments
        FROM [reddit_posts]
        WHERE author <> '[deleted]'
        GROUP BY 1,2 
    ) 
  ) 
)
GROUP BY 1,2
```
### API Reference
(For possibly reusable functions)
> ```make_report_csv.leaderboard(pandas.DataFrame df)``` [source](https://github.com/chunchuck2000/reddit_posts/blob/master/make_report_csv.py#L5)

Parameters:
* df - pandas.DataFrame with structure described in [Data Structure](https://github.com/chunchuck2000/reddit_posts/blob/master/DESGIN_DOC.md#data-structure) 

Returns:
* pandas.DataFrame with columns:
```
post_date
subreddit
author
score            - author's score accumulated on post_date in subreddit
num_comments     - number of comments on author's post on post_date in subreddit
num_posts        - author's number of posts submitted to subreddit on post_date
daily_rank       - author's rank on post_date in subreddit
daily_total_rank - total number of authors posted on post_date in subreddit
```

> ```make_report_csv.sub_streak(pandas.DataFrame df)``` [source](https://github.com/chunchuck2000/reddit_posts/blob/master/make_report_csv.py#L52)

Parameters:
* df - pandas.DataFrame with structure described in [Data Structure](https://github.com/chunchuck2000/reddit_posts/blob/master/DESGIN_DOC.md#data-structure) 

Returns:
* pandas.DataFrame with columns:
```
subreddit
author
score            - author's score accumulated in subreddit during submission streak
num_comments     - number of comments on author's post in subreddit during submission streak
num_posts        - author's number of posts submitted to subreddit during submission streak
streak_group     - author's submission streak grouping index
streak_start     - author's submission streak start date
streak_length    - author's submission streak length in days
```
