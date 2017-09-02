import make_report_csv
import pandas as pd

def _test_leaderboard():
    test_data = [
        {'post_date': 0, 'subreddit': 'all','author': 'u1','num_comments':2, 'score': 2},
        {'post_date': 0, 'subreddit': 'all','author': 'u1','num_comments':2, 'score': 2},
        {'post_date': 0, 'subreddit': 'funny','author': 'u1','num_comments': 2, 'score': 2},
        {'post_date': 0, 'subreddit': 'funny','author': 'u1','num_comments': 2, 'score': 2},
        {'post_date': 0, 'subreddit': 'funny','author': 'u2','num_comments': 2, 'score': 2},
        {'post_date': 0, 'subreddit': 'funny','author': 'u2','num_comments': 3, 'score': 2},
        {'post_date': 0, 'subreddit': 'funny','author': 'u3','num_comments': 1, 'score': 1},
        {'post_date': 0, 'subreddit': 'funny','author': 'u3','num_comments': 1, 'score': 1},
        {'post_date': 0, 'subreddit': 'funny','author': 'u3','num_comments': 2, 'score': 2},
        {'post_date': 0, 'subreddit': None,'author': 'u1','num_comments': 2, 'score': 2},
    ]
    l = make_report_csv.leaderboard(pd.DataFrame(test_data))

    assert len(l) == 4
    assert len(l.loc[(l.subreddit == 'all')]) == 1
    assert len(l.loc[(l.subreddit == 'funny')]) == 3

    assert len(l.loc[(l.subreddit == 'funny') & (l.author == 'u1') & (l.daily_rank == 3)]) == 1
    assert len(l.loc[(l.subreddit == 'funny') & (l.author == 'u2') & (l.daily_rank == 2)]) == 1
    assert len(l.loc[(l.subreddit == 'funny') & (l.author == 'u3') & (l.daily_rank == 1)]) == 1

    assert len(l.loc[(l.subreddit == 'funny') & (l.author == 'u1') & (l.daily_total_rank == 3)]) == 1
    assert len(l.loc[(l.subreddit == 'funny') & (l.author == 'u2') & (l.daily_total_rank == 3)]) == 1
    assert len(l.loc[(l.subreddit == 'funny') & (l.author == 'u3') & (l.daily_total_rank == 3)]) == 1

    assert len(l.loc[(l.subreddit == 'funny') & (l.author == 'u3') & (l.num_posts == 3)]) == 1
    assert len(l.loc[(l.subreddit == 'funny') & (l.author == 'u3') & (l.num_comments == 4)]) == 1
    assert len(l.loc[(l.subreddit == 'funny') & (l.author == 'u3') & (l.score == 4)]) == 1
    
    print('make_report_csv.leaderboard tests passed')

def _test_sub_streak():
    test_data = [
        {'post_date': 0,            'subreddit': 'all','author': 'u1','num_comments':2, 'score': 2},
        {'post_date': 60*60*24,     'subreddit': 'all','author': 'u1','num_comments':2, 'score': 1},
        {'post_date': 2*60*60*24,   'subreddit': 'all','author': 'u1','num_comments':2, 'score': 2},
        {'post_date': 4*60*60*24,   'subreddit': 'all','author': 'u1','num_comments':2, 'score': 1},
        {'post_date': 5*60*60*24,   'subreddit': 'all','author': 'u1','num_comments':2, 'score': 2},
        {'post_date': 0,            'subreddit': None,'author': 'u1','num_comments':2, 'score': 1}
    ]
    s = make_report_csv.sub_streak(pd.DataFrame(test_data))

    assert len(s) == 2
    
    assert len(s.loc[(s.streak_start == '1970-01-01') & (s.streak_length == 3)]) == 1
    assert len(s.loc[(s.streak_start == '1970-01-01') & (s.num_comments == 8)]) == 1
    assert len(s.loc[(s.streak_start == '1970-01-01') & (s.num_posts == 4)]) == 1
    assert len(s.loc[(s.streak_start == '1970-01-01') & (s.score == 6)]) == 1

    assert len(s.loc[(s.streak_start == '1970-01-05') & (s.streak_length == 2)]) == 1
    assert len(s.loc[(s.streak_start == '1970-01-05') & (s.num_comments == 4)]) == 1
    assert len(s.loc[(s.streak_start == '1970-01-05') & (s.num_posts == 2)]) == 1
    assert len(s.loc[(s.streak_start == '1970-01-05') & (s.score == 3)]) == 1

    print('make_report_csv.sub_streak tests passed')

if __name__ == "__main__":
   _test_leaderboard()
   _test_sub_streak()