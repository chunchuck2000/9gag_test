import pandas as pd
import os.path
from datetime import datetime as dt

def leaderboard(r_posts):
    """Calculates daily user ranking of each subreddit.
    Based on a user's daily number of posts, number of comments and score received.

    Takes pandas DF, each row is one post, with columns
    | post_date | subreddit | author | num_comments | score |
    
    Returns pandas DF, with columns
    | post_date | subreddit | author | score | num_comments | num_posts | daily_rank | daily_total_rank |
    """

    r_leaderboard = r_posts[-r_posts.subreddit.isnull()].groupby([
                                        'post_date',
                                        'subreddit',
                                        'author'
                                    ]).agg({
                                        'author':'count',
                                        'num_comments':'sum',
                                        'score':'sum'
                                    })
    
    # rename a column
    r_leaderboard.columns = ['num_posts' if c == 'author' else c for c in r_leaderboard.columns]
    r_leaderboard.reset_index(inplace=True)
    
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

    
    r_leaderboard['daily_total_rank'] = r_leaderboard.groupby([
                                        'post_date', 
                                        'subreddit'
                                    ])['author'].transform(pd.Series.nunique)

    # convert Epoch (int) to datetime
    r_leaderboard['post_date'] = pd.to_datetime(r_leaderboard['post_date'] ,unit='s')
    return r_leaderboard

def sub_streak(r_posts):
    """Calculates a user's day to day reddit submission streak
    
    Takes pandas DF, each row is one post, with columns
    | post_date | subreddit | author | num_comments | score |

    Returns pandas DF, with columns
    | author | streak_group | num_posts | score | num_comments | streak_length | streak_start |
    """

    r_sub_streak = r_posts.groupby([
                            'post_date',
                            'author'
                        ]).agg({
                            'author': 'count',
                            'num_comments': 'sum',
                            'score': 'sum'
                        })

    # rename a column
    r_sub_streak.columns = ['num_posts' if c == 'author' else c for c in r_sub_streak.columns]
    r_sub_streak.reset_index(inplace=True)

    r_sub_streak['post_order'] = r_sub_streak.sort_values('post_date').groupby('author').cumcount()

    # calculate each streak group by:
    r_sub_streak['streak_group'] = r_sub_streak['post_date'] - r_sub_streak['post_order']*(60*60*24)

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
    
    r_sub_streak['post_date'] = pd.to_datetime(r_sub_streak['post_date'] ,unit='s')
    
    # rename a column
    r_sub_streak.columns = ['streak_start' if c == 'post_date' else c for c in r_sub_streak.columns]
    return r_sub_streak

def _make_leaderboard_and_streak_csv():
    # reads csv file
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
    r_posts = df.loc[(df.author != '[deleted]'),columns]

    # truncate Epoch timestamps into nearest day, day in seconds = 60*60*24
    r_posts['post_date'] = r_posts['created_utc'] - r_posts['created_utc']%(60*60*24)

    print_log('Making leaderboard report csv...')

    r_leaderboard = leaderboard(r_posts)

    # Top 10 leaderboard, export to csv
    leaderboard_csv_filename = 'reddit_posts_2016_09_week_1_leaderboard_top_10.csv'
    r_leaderboard.loc[(r_leaderboard.daily_rank <= 10)].sort_values([
                                        'subreddit',
                                        'post_date',
                                        'daily_rank'
                                    ]).to_csv(leaderboard_csv_filename, index=False)


    print_log('Making submission streak report csv...')

    r_sub_streak = sub_streak(r_posts)

    # to csv
    streak_csv_filename = 'reddit_posts_2016_09_week_1_streak.csv'
    r_sub_streak.loc[(r_sub_streak.streak_length >= 2)] .sort_values([
                                'streak_length', 
                                'num_posts', 
                                'streak_start', 
                                'score', 
                                'num_comments', 
                                'author'
                            ], ascending=[ 
                                False, False, True, False, False, True
                            ]).to_csv(streak_csv_filename, index=False)

    print_log("Done!")

if __name__ == "__main__":
   _make_leaderboard_and_streak_csv()
