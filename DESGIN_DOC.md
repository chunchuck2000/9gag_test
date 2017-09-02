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
Currently a CSV of the data from [Reddit Posts Data](https://bigquery.cloud.google.com/dataset/fh-bigquery:reddit_posts) 
is ingested using pandas, the leaderboard and submission streak is then calculated and saved to two CSVs 
(using ```make_report_csv.py```), which can be viewed later (using ```leaderboard.html``` and ```streak.html```).

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
