# Note on the data

The text in `corpus.jsonl.gz` and `comments.jsonl` is public Reddit content (post titles, self-text, and comment bodies) retrieved from the [Arctic Shift](https://arctic-shift.photon-reddit.com) archive, a free public Reddit archive run by a Pushshift successor.

- **No usernames or other author identifiers were collected.** Each record holds only an id, the subreddit, a timestamp, a score, the text, and a permalink.
- The text belongs to its original Reddit authors. It is included here for research and transparency, so readers can check the analysis against the source. Permalinks are included so any item can be traced back to Reddit.
- If you are an author and want a specific item removed, open an issue.
- The code in this repository is MIT licensed (see `LICENSE`). That license covers the scripts, not the Reddit text.

Collected for a one-time analysis. Not affiliated with Reddit or Arctic Shift.
