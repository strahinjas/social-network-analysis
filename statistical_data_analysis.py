import pandas as pd


def set_from_column(column, *data_frames):
    result = set()

    for data_frame in data_frames:
        result |= set(data_frame[column].unique())

    return result


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


def comment_count(submissions, comments):
    grouped_comments = comments.groupby("link_id").size().reset_index(name="count")
    grouped_comments["link_id"] = grouped_comments["link_id"].str.slice(3)

    result = pd.concat([submissions.set_index("submission_id"), grouped_comments.set_index("link_id")],
                       axis=1, join="inner").reset_index()

    return result.sort_values("count", ascending=False)


submissions = pd.read_pickle("dataset/cleaned/submissions")
comments = pd.read_pickle("dataset/cleaned/comments")

subreddits = groupby_and_count("subreddit", "author", submissions, comments)

print(f"Number of subreddits: {len(subreddits)}\n")

print(f"Subreddits with most users:\n{subreddits.iloc[0:10]}\n")
print(f"Subreddits with most comments:\n{comments['subreddit'].value_counts().iloc[0:10]}\n")

print(f"Average users per subreddit: {subreddits['author'].mean()}\n")

print(f"Users with most submissions:\n{user_count(submissions).iloc[0:10]}\n")
print(f"Users with most comments:\n{user_count(comments).iloc[0:10]}\n")

print(f"Most active users:\n{groupby_and_count('author', 'subreddit', submissions, comments).iloc[0:10]}\n")

print("Submissions with most comments:")
with pd.option_context("display.max_rows", None, "display.max_columns", None):
    print(comment_count(submissions, comments).iloc[0:10])
