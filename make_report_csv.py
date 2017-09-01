import pandas as pd
import os.path
from datetime import datetime as dt

gz_filename = 'reddit_posts_2016_09_week_1.csv.gz'

def print_log(msg):
    print("[{}] {}".format(dt.now().strftime('%Y-%m-%d %H:%M:%S'), msg))

if os.path.isfile(gz_filename):
    print_log("Reading {} ...".format(gz_filename))
    df = pd.read_csv(gz_filename, compression='gzip')
else:
    raise FileNotFoundError("{} not found".format(gz_filename))

# columns needed
columns = [
            'created_utc',
            'subreddit',
            'author',
            'num_comments',
            'score'
          ]

# user centric analysis, ignore deleted users
r_posts = df.ix[:,columns][df.author != '[deleted]']

# truncate Epoch timestamps into nearest day
r_posts['post_date'] = r_posts['created_utc'] - r_posts['created_utc']%(60*60*24)

# for calculating number of posts, SUM(num_posts)
r_posts['num_posts'] = 1


# r_post: 1 row = 1 post
# post_date:    post creation timestamp (seconds)
# subreddit:    subreddit name
# author:       reddit user
# num_comments: number of comments on the post
# score:        upvotes - downvotes of the post

# Leaderboard

print_log('Making leaderboard report csv...')

# get daily number of posts, number of comments and score 
# for each subreddit and author
r_leaderboard = r_posts[-r_posts.subreddit.isnull()].groupby([
                                    'post_date',
                                    'subreddit',
                                    'author'
                                ]).agg({
                                    'num_posts':sum,
                                    'num_comments':sum,
                                    'score':sum
                                }).reset_index()
        
# rank each author in each subreddit and day
# by number of posts, number of comments, score and author's name
r_leaderboard['daily_rank'] = r_leaderboard.sort_values([
                                    'num_posts',
                                    'score',
                                    'num_comments',
                                    'author'
                                ], ascending = [
                                    False,False,False,True
                                ]).groupby([
                                    'post_date',
                                    'subreddit'
                                ]).cumcount() + 1

# total number of authors who submitted, for each day and subreddit
r_leaderboard['daily_total_rank'] = r_leaderboard.groupby([
                                    'post_date', 
                                    'subreddit'
                                ])['author'].transform(pd.Series.nunique)

# convert Epoch (int) to datetime
r_leaderboard['post_date'] = pd.to_datetime(r_leaderboard['post_date'] ,unit='s')

# Top 10 leaderboard, export to csv
leaderboard_csv = 'reddit_posts_2016_09_week_1_leaderboard_top_10.csv'
r_leaderboard.loc[(r_leaderboard.daily_rank <= 10)].sort_values([
                                    'subreddit',
                                    'post_date',
                                    'daily_rank'
                                ]).to_csv(leaderboard_csv, index=False)


# Submission Streak

print_log('Making submission streak report csv...')

# get daily number of posts, number of comments and score 
# for each author
r_sub_streak = r_posts.groupby([
                        'post_date',
                        'author'
                    ]).agg({
                        'num_posts':sum,
                        'num_comments':sum,
                        'score':sum
                    }).reset_index()

# ordering of days with submission for each author
r_sub_streak['post_order'] = r_sub_streak.sort_values('post_date').groupby('author').cumcount() + 1

# each author's earliest posting date
r_sub_streak['first_post_date'] = r_sub_streak.groupby('author')['post_date'].transform(pd.Series.min)

# calculate each streak group by:
# post_order - day_diff(post_date - first_post_date)
r_sub_streak['streak_group'] = r_sub_streak['post_order']*(60*60*24) \
                                - (r_sub_streak['post_date']-r_sub_streak['first_post_date'])

r_sub_streak['streak_length'] = 1

r_sub_streak = r_sub_streak.groupby([
                        'author',
                        'streak_group'
                    ]).agg({
                        'streak_length':sum,
                        'post_date':min,
                        'num_posts':sum,
                        'num_comments':sum,
                        'score':sum,
                    }).reset_index()
    
r_sub_streak['streak_start'] = pd.to_datetime(r_sub_streak['post_date'] ,unit='s')
del r_sub_streak['post_date']

# to csv
streak_csv = 'reddit_posts_2016_09_week_1_streak.csv'
r_sub_streak.loc[(r_sub_streak.streak_length >= 2)] .sort_values([
                            'streak_length', 
                            'num_posts', 
                            'streak_start', 
                            'score', 
                            'num_comments', 
                            'author'
                        ], ascending=[ 
                            False, False, True, False, False, True
                        ]).to_csv(streak_csv, index=False)

print_log("Done!")