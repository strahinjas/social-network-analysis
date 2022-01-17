import pandas as pd
import glob

comments_path = "dataset/reddit_comments_2008"
submissions_path = "dataset/reddit_submissions_2008"


def read_data(directory):
    all_files = glob.glob(directory + "/*.csv")
    frames = []

    for month, filename in enumerate(all_files):
        frame = pd.read_csv(filename, index_col=0, low_memory=False)
        frame["month"] = month + 1
        frames.append(frame)

    return pd.concat(frames, ignore_index=True)


def clean_submissions(submissions):
    print(submissions["id"].isnull().values.any())
    print(submissions["id"].is_unique)

    submissions = submissions.drop(["created_utc", "url", "permalink", "domain", "distinguished"], axis=1)

    print(submissions)
    print(submissions.shape)

    submissions = submissions[submissions["author"] != "[deleted]"]

    submissions = submissions.rename(columns={"id": "submission_id"})
    submissions["id"] = submissions.index

    return submissions


submissions_df = read_data(submissions_path)
submissions_df = clean_submissions(submissions_df)

comments_df = read_data(comments_path)

