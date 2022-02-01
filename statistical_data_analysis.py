import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import pearsonr


def groupby_and_count(groupby_column, aggregate_column, *data_frames):
    data_frame = pd.concat(data_frames, ignore_index=True)

    grouped_data_frame = data_frame.groupby(groupby_column)
    grouped_data_frame = grouped_data_frame.agg({aggregate_column: "nunique"})
    grouped_data_frame = grouped_data_frame.reset_index()
    grouped_data_frame = grouped_data_frame.sort_values(aggregate_column, ascending=False)

    return grouped_data_frame


def user_count(data_frame):
    grouped_data_frame = data_frame.groupby("author").size().reset_index(name="count")
    grouped_data_frame = grouped_data_frame.sort_values("count", ascending=False)
    return grouped_data_frame


def pearson_correlation(submissions_data_frame, comments_data_frame):
    grouped_submissions = submissions_data_frame.groupby("author").size().reset_index(name="submission_count")
    grouped_comments = comments_data_frame.groupby("author").size().reset_index(name="comment_count")

    result = pd.concat([grouped_submissions.set_index("author"), grouped_comments.set_index("author")],
                       axis=1, join="outer").reset_index()

    result = result.fillna(0)

    plt.scatter(result["submission_count"], result["comment_count"])

    corr, _ = pearsonr(result["submission_count"], result["comment_count"])
    print("Pearson correlation coefficient: %.5f" % corr)

    plt.title("Pearson correlation coefficient: %.5f" % corr)
    plt.xlabel("Submission Count")
    plt.ylabel("Comment Count")

    plt.savefig(fname="figures/pearson.png")


def comment_count(submissions, comments):
    grouped_comments = comments.groupby("link_id").size().reset_index(name="count")
    grouped_comments["link_id"] = grouped_comments["link_id"].str.slice(3)

    result = pd.concat([submissions.set_index("submission_id"), grouped_comments.set_index("link_id")],
                       axis=1, join="inner").reset_index()

    return result.sort_values("count", ascending=False)


def subreddit_analysis(submissions, comments):
    subreddits = groupby_and_count("subreddit", "author", submissions, comments)

    print(f"Number of subreddits: {len(subreddits)}\n")

    most_users = subreddits.iloc[0:10]
    print(f"Subreddits with most users:\n{most_users}\n")
    most_users.to_csv("result_tables/subreddit_most_users.csv")

    most_comments = comments['subreddit'].value_counts().iloc[0:10]
    print(f"Subreddits with most comments:\n{most_comments}\n")
    most_comments.to_csv("result_tables/subreddit_most_comments.csv")

    print(f"Average users per subreddit: %.5f\n" % subreddits['author'].mean())


def user_analysis(submissions, comments):
    most_submissions = user_count(submissions).iloc[0:10]
    print(f"Users with most submissions:\n{user_count(submissions).iloc[0:10]}\n")
    most_submissions.to_csv("result_tables/user_most_submissions.csv")

    most_comments = user_count(comments).iloc[0:10]
    print(f"Users with most comments:\n{user_count(comments).iloc[0:10]}\n")
    most_comments.to_csv("result_tables/user_most_comments.csv")

    most_active_users = groupby_and_count('author', 'subreddit', submissions, comments).iloc[0:10]
    print(f"Most active users:\n{most_active_users}\n")
    most_active_users.to_csv("result_tables/most_active_users.csv")

    pearson_correlation(submissions, comments)


def submission_analysis(submissions, comments):
    print("\nSubmissions with most comments:")
    with pd.option_context("display.max_rows", None, "display.max_columns", None):
        submission_most_comments = comment_count(submissions, comments).iloc[0:10]
        print(submission_most_comments)
        submission_most_comments.to_csv("result_tables/submission_most_comments.csv")


def analyze():
    submissions = pd.read_pickle("dataset/cleaned/submissions")
    comments = pd.read_pickle("dataset/cleaned/comments")

    subreddit_analysis(submissions, comments)
    user_analysis(submissions, comments)
    submission_analysis(submissions, comments)


analyze()
