# Vibe-coded site "tells": data and graphs

Companion data for the Reddit post. Everything here is reproducible from the scripts in this folder against the Arctic Shift public Reddit archive (no API key).

## Dataset

- **3,214,533 posts scanned** across **47 subreddits** that were full-text searched (2020 to 2026). The **46,971** on-topic posts below are 1.46% of that scanned base.
- **46,971** unique on-topic posts + **3,033** comments from **125** canonical "why do AI sites all look the same / dead giveaways" threads.
- **47 subreddits** represented (AI-tool, model, design, frontend, no-code, indie, SaaS), 2020 to 2026. The run list held 49 names: r/v0dev does not exist, and r/GeminiAI exists (47,048 posts) but was excluded from the tell harvest, so it is not in the scanned 47.
- Top on-topic subs by volume: SideProject (3,311), SaaS (3,146), vibecoding (2,710), ChatGPT (2,613), ClaudeAI (2,259), microsaas (2,156), ArtificialInteligence (1,993), webdev (1,886), indiehackers (1,784), LocalLLaMA (1,769).
- Design-context subset (posts whose text carries visual/appearance vocabulary): **32,822** (69.9% of corpus); 29.5% of those carry negative-aesthetic sentiment.

## Method (reading rule)

Share of posts or comments, not raw counts, because the topic barely existed before 2024 and raw counts mostly track subreddit growth. A tell that recurs across many threads ranks above one that spikes in a single viral thread. Two signals are reported:

- **Comment share** = share of the 3,033 on-topic comments naming the tell. This is the cleanest signal (100% on-topic) and the primary ranking.
- **Post share** = share of the 32,822 design-context posts mentioning the tell. Broader, noisier, used as a secondary check.

Each tell was then adversarially verified by an independent agent (is it real, is it visual, false-positive risk, best verbatim quote). 11 of 12 top tells confirmed; mesh/blob/aurora rejected as a keyword artifact.

## Ranked tells (master table)

| Rank | Tell | Comment share | Post share | FP risk | Verdict |
|---|---|---|---|---|---|
| - | "All looks the same" / cookie-cutter (umbrella) | 6.1% | 13.1% (91% neg) | low | confirmed, top finding |
| - | "Screams AI" / soulless / slop (umbrella) | 6.4% | 13.0% | medium | confirmed, umbrella label |
| 1 | Default shadcn / Tailwind kit | 2.5% | 2.2% | medium | confirmed, top concrete cause |
| 2 | Purple / violet ("AI purple") | 2.3% | 0.7% | low | confirmed, top color tell |
| 3 | Gradients / gradient hero text | 2.0% | 1.2% | low | confirmed (share understates it) |
| 4 | Too many animations / Framer fade-ins | 1.1% | 2.0% | high | confirmed but minor/noisy |
| 5 | Rounded corners / pill buttons | 0.8% | 0.5% | medium | confirmed |
| 6 | Dark mode + neon glow | 0.7% | 1.3% | low | confirmed |
| 7 | Emoji as icons / sparkles / rockets | 0.5% | 2.7% | medium | confirmed (emoji-as-icons) |
| 8 | Generic sans font (Inter / Geist) | 0.4% | 0.4% | low | confirmed (share understates it) |
| 9 | Symmetric hero + 3 feature cards + CTA | 0.4% | 1.6% | medium | confirmed, thin |
| - | Stock illustrations / clipart | 0.2% | 0.9% | - | not individually verified |
| - | Same hero: huge headline + 2 buttons | 0.2% | 0.6% | - | folded into #9 |
| - | Glassmorphism / frosted glass | 0.2% | 0.3% | - | minor |
| - | Mesh / blob / aurora backgrounds | 0.3% | 0.6% | - | REJECTED (keyword artifact) |
| - | Bento grid | 0.1% | 0.1% | - | last, contested even by complainers |

Headline correction vs. the usual Twitter list: bento grids and mesh/aurora gradients, the stereotypical "AI design" memes, are near the bottom or rejected. What Reddit actually harps on is generic sameness, the default shadcn/Tailwind kit, and purple gradients.

## Topic growth (growth-normalized)

| Year | vibe-coding posts | total posts (all subs) | per 10k posts |
|---|---|---|---|
| 2020 | 7 | 83,355 | 0.84 |
| 2021 | 15 | 95,214 | 1.58 |
| 2022 | 42 | 200,509 | 2.09 |
| 2023 | 52 | 286,851 | 1.81 |
| 2024 | 17,225 | 619,811 | 277.91 |
| 2025 | 17,726 | 527,641 | 335.95 |

A ~150x jump from 2023 to 2024. This is why share-of-posts matters: raw counts would conflate the topic exploding with subs simply growing.

## Charts

Original five:
- `chart_tells_comment.png` — ranked tells by comment share (the honest, on-topic ranking).
- `chart_post_vs_comment.png` — post vs comment signal per specific tell (shows the emoji and feature-card inflation at post level).
- `chart_tells_ranked.png` — post-level ranking (secondary).
- `chart_growth.png` — topic growth, per 10k posts/year.
- `chart_tell_trend.png` — top tells, share by year.

Scale and count graphs (numbers, not shares):
- `chart_scanned_by_sub.png` — total posts scanned in each of the 47 subreddits; grand total 3,214,533 in the title.
- `chart_raw_counts_by_tell.png` — raw number of posts and comments matching each tell (the numerators), with the combined total per tell. Comment counts are the cleaner signal.
- `chart_funnel.png` — how 3.21M scanned narrows to 46,971 on-topic, 32,822 design-context, 3,033 canonical-thread comments.
- `chart_concentration.png` — on-topic posts as a share of each sub's own volume; r/lovable leads near 9%, giants sit near 0.5%.
- `chart_cooccurrence.png` — heatmap of how often two tells are named in the same comment; purple and gradients co-occur 32 times, the strongest pair.
- `chart_sentiment_by_tell.png` — negative-sentiment share per tell (post-level, keyword-based).
- `chart_top_threads.png` — the canonical threads behind the comment signal by upvotes; "dead giveaways for AI slop websites" leads at 2,445.

## Coverage and blocked sources

- 47 of 49 run-list subs were full-text searched and represented in the corpus, including the giants (r/ChatGPT 526k, r/SideProject 373k, r/webdev 335k).
- r/v0dev does not exist (0 posts). r/GeminiAI exists (47,048 posts) but was on the harvest skip list, so it was counted for scale only and is not in the scanned 47 or the on-topic corpus.
- The aggregate endpoint timed out on the largest subs (r/ChatGPT, r/artificial, r/webdev, r/SideProject, r/ArtificialInteligence) during the run; their totals were recovered afterward with backoff. Full-text search itself worked on every sub, so the documented "422 on very active subs" gotcha did not trigger here.

## File index

- `collect.py` — Phase 1-2 aggregate counts (totals + matched by year).
- `harvest.py` — Phase 3 resumable post-text harvester (the fixed one).
- `harvest_comments.py` — comment harvester for the 125 canonical threads.
- `analyze.py` / `analyze_comments.py` — tell tabulation (post-level / comment-level).
- `make_charts.py` / `make_charts2.py` — the original five charts / the seven scale-and-count charts.
- `post_workflow.js` — adversarial verification + draft/judge workflow.
- Data: `corpus.jsonl`, `comments.jsonl`, `totals_by_year.csv`, `matched_by_year.csv`.
- Tables: `tell_counts.csv`, `comment_tell_counts.csv`, `tell_share_by_year.csv`, `growth_by_year.csv`, `scanned_totals_by_sub.csv`, `summary.txt`.
- Quote banks (verbatim + permalinks): `tell_examples.md`, `comment_tell_examples.md`.
