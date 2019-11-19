import praw
import configparser

def rewrite_comment(comment):
    comment.edit(".")

def save_comment(comment):
    print("{} : {}".format(comment.permalink, comment.body))

def save_submission(submission):
    print("{} : {}".format(submission.permalink, submission.title))

def save_upvoted(submission):
    save_submission(submission)

def save_comment_summary(comment):
    print("{} : {}".format(comment.permalink, comment.body[:20]))

def save_saved(saved):
    if isinstance(saved, praw.models.Comment):
        save_comment_summary(saved)
    elif isinstance(saved, praw.models.Submission):
        save_submission(saved)

def get_credentials():
    config = configparser.ConfigParser()
    config.read('credentials.ini')
    return config['reddit']

def main():
    reddit = praw.Reddit(**get_credentials())

    for comment in reddit.user.me().comments.new():
        save_comment(comment)
        rewrite_comment(comment)
        comment.delete()

    for submission in reddit.user.me().submissions.new():
        save_submission(submission)
        submission.delete()

    for upvoted in reddit.user.me().upvoted():
        save_upvoted(upvoted)

    for saved in reddit.user.me().saved():
        save_saved(saved)

if __name__ == "__main__":
    main()
