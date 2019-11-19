import arrow
import configparser
import json
import os
import praw
import argparse


def get_credentials(config_filename):
    config = configparser.ConfigParser()
    config.read(config_filename)
    return config['reddit']


def setup_folder_structure(username):
    ret = {
        "submissions": "{}/submissions/".format(username),
        "comments": "{}/comments/".format(username),
        "upvoted": "{}/upvoted/".format(username),
        "saved": "{}/saved/".format(username)
    }
    os.makedirs(ret['submissions'], exist_ok=True)
    os.makedirs(ret['comments'], exist_ok=True)
    os.makedirs(ret['upvoted'], exist_ok=True)
    os.makedirs(ret['saved'], exist_ok=True)

    return ret


def archive_mode(reddit, folder_structure):
    def save_json(filename, fmt, it):
        with open(filename, 'w') as f:
            entities = []
            for entity in it:
                entities.append(fmt(entity))
            json.dump(entities, f)

    def fmt_comment(comment):
        created_utc = arrow.get(comment.created_utc)
        return {
            "body": comment.body,
            "permalink": comment.permalink,
            "created_utc": created_utc.isoformat(),
        }

    def fmt_submission(submission):
        created_utc = arrow.get(submission.created_utc)
        return {
            "title": submission.title,
            "permalink": submission.url,
            "created_utc": created_utc.isoformat(),
            "selftext": submission.selftext,
        }

    def summarise(text):
        if len(text) > 50:
            return text[:50] + "..."
        return text

    def fmt_submission_summary(submission):
        created_utc = arrow.get(submission.created_utc)
        return {
            "title": submission.title,
            "permalink": submission.url,
            "created_utc": created_utc.isoformat(),
            "selftext_summary": summarise(submission.selftext),
        }

    def fmt_comment_summary(comment):
        created_utc = arrow.get(comment.created_utc)
        return {
            "body": summarise(comment.body),
            "permalink": comment.permalink,
            "created_utc": created_utc.isoformat(),
        }

    def fmt_saved(saved):
        if isinstance(saved, praw.models.Comment):
            return fmt_comment_summary(saved)
        elif isinstance(saved, praw.models.Submission):
            return fmt_submission_summary(saved)

    def save_comments():
        comments_filename = os.path.join(folder_structure['comments'], 'posts')
        print("saving all comments to {}".format(comments_filename))
        save_json(comments_filename,
                  fmt_comment,
                  reddit.user.me().comments.new())

    def save_submissions():
        submissions_filename = os.path.join(
                folder_structure['submissions'], 'posts')
        print("saving all submissions to {}".format(submissions_filename))
        save_json(submissions_filename,
                  fmt_submission,
                  reddit.user.me().submissions.new())

    def save_upvoted():
        upvoted_filename = os.path.join(folder_structure['upvoted'], 'posts')
        print("saving all upvoted submissions to {}".format(upvoted_filename))
        save_json(upvoted_filename,
                  fmt_submission_summary,
                  reddit.user.me().upvoted())

    def save_saved():
        saved_filename = os.path.join(folder_structure['saved'], 'posts')
        print("saving all saved posts to {}".format(saved_filename))
        save_json(saved_filename, fmt_saved, reddit.user.me().saved())

    save_comments()
    save_submissions()
    save_upvoted()
    save_saved()


def shred_mode(reddit):
    print("deleting all comments")
    for comment in reddit.user.me().comments.new():
        comment.edit(".")
        comment.delete()

    print("deleting all submissions")
    for submission in reddit.user.me().submissions.new():
        submission.delete()


def main():
    parser = argparse.ArgumentParser(
        description="command line arguments for this script")
    parser.add_argument(
        "-c", "--config",
        help="Configuration file", default="credentials.ini")
    parser.add_argument(
        "-d", "--shred",
        help="Run Shred mode: delete all comments and submissions.",
        action="store_true")
    parser.add_argument(
        "-a", "--archive",
        help="Write shreddit and praw config files to current directory.",
        action="store_true")
    args = parser.parse_args()

    print("logging in using credentials found in {}".format(args.config))
    reddit = praw.Reddit(**get_credentials(args.config))

    if args.archive:
        folder_structure = setup_folder_structure(reddit.user.me().name)
        archive_mode(reddit, folder_structure)

    if args.shred:
        shred_mode(reddit)


if __name__ == "__main__":
    main()
