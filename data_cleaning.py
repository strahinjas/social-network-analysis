import glob
import pandas as pd


def read_data(directory):
    data_files = glob.glob(directory + "/*.csv")
    data_frames = []

    for month, filename in enumerate(data_files):
        data_frame = pd.read_csv(filename, index_col=0, low_memory=False)
        data_frame["month"] = month + 1
        data_frames.append(data_frame)

    return pd.concat(data_frames, ignore_index=True)


def clean_data(data_frame, columns_to_drop, name_id):

    data_frame = data_frame[data_frame["id"].notnull()]
    data_frame = data_frame.drop(columns_to_drop, axis=1)
    data_frame = data_frame[data_frame["author"] != "[deleted]"]
    data_frame = data_frame.rename(columns={"id": name_id})

    data_frame.reset_index(drop=True, inplace=True)
    data_frame["id"] = data_frame.index

    print(data_frame.dtypes)
    print(data_frame)
    print(data_frame.shape)

    return data_frame


def export_cleaned_data(data_frame, filename):
    data_frame.to_csv(f"dataset/cleaned/{filename}.csv", index=False)
    data_frame.to_pickle(f"dataset/cleaned/{filename}")


def prepare_data():
    submissions_path = "dataset/reddit_submissions_2008"
    comments_path = "dataset/reddit_comments_2008"

    submissions_columns = ["created_utc", "url", "permalink", "domain", "distinguished"]
    comments_columns = ["created_utc", "distinguished", "controversiality"]

    submissions = read_data(submissions_path)
    submissions = clean_data(submissions, submissions_columns, "submission_id")

    comments = read_data(comments_path)
    comments = clean_data(comments, comments_columns, "comment_id")

    export_cleaned_data(submissions, "submissions")
    export_cleaned_data(comments, "comments")


prepare_data()
