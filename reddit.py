import praw

reddit = praw.Reddit(
    client_id="NZ-kHJ34bIRkpJGZ8rDomg",
    client_secret="kyep9hfv9vTdPfbg5XU3r_0qvRo1Wg",
    user_agent="Readit Reader",
)

def get_submissions(sub):
    print("[Reddit] Fetching submission (this may take a few seconds)")
    return list(reddit.subreddit(sub).top(limit=10, time_filter="day"))        
def get_comments(submission):
    print("[Reddit] Fetching comments (this may take a few seconds)")
    return list(submission.comments)