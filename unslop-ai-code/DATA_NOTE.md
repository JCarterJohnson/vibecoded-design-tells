# Data note

The text in `corpus.jsonl` and `comments.jsonl` is public Reddit content,
collected through the free [Arctic Shift](https://arctic-shift.photon-reddit.com)
archive (a Pushshift successor). It belongs to the people who wrote it.

- **No usernames were collected.** Each record keeps only: id, subreddit,
  created_utc, score, num_comments, title/selftext (or comment body), permalink,
  and the intent phrase that matched it.
- Bodies are truncated (posts to ~3,500 chars, comments to ~2,200) — enough to
  detect and quote the tells, not to mirror whole threads.
- This is a **proxy for vocal, online opinion**, not a measurement of all code or
  all developers. Trust the relative ordering of the tells more than the exact
  percentages. Small subreddits are noisy, and keyword matching can miss sarcasm
  or catch the wrong sense of a word.
- The aggregate "scanned base" denominators are best-effort: Arctic Shift's
  aggregate endpoint times out on the busiest subreddits, so per-sub totals exist
  only where the archive would return them. The tell ranking itself is a share of
  the on-topic corpus and does not depend on those denominators.

If you are an author and want a quote removed, open an issue.
