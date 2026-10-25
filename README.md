# story-miner

An AI research partner that finds the stories worth telling.

The creator's problem is never a shortage of ideas — it's separating the
one story that matters from sixty that don't. This tool does that with
**three gates, in order**:

1. **NUMBER** — the item carries a figure, threshold, or metric. No number,
   no story. Claims need receipts.
2. **FOLK** — the crowd reads it wrong. Contrarian framing, an ignored
   implication, a belief the item quietly contradicts.
3. **FRESH** — it isn't already a listicle. If the internet already wrote
   "17 tools to...", the angle is taken.

Output: three story briefs max — the number, the link, the folk line, the
angle, and a draft title you're meant to argue with. The breed of output
is a *brief*, not a draft: judgment stays with the person who signs the work.

## Run

```bash
python3 src/miner.py --feeds feeds.txt --out docs
# → docs/<date>-briefs.md
```

Public RSS only. Zero API keys. Swap feeds to point at any market.

## Tested

Live run over 7 public feeds:
60-item pool · 3-gate filter · briefing committed to `docs/`
(raises, funding rounds, and market-shift items surfaced — the daily
listicle noise filtered out).

## Disciplines

- **Three briefs max.** If everything survives, the gates failed.
- **A brief is not a draft.** The tool finds and frames; the human writes.
- **Silence is a valid result.** An empty day ships anyway — the gates hold.

## Roadmap

- [ ] Reddit JSON integration for discussion-pool angles
- [ ] angle-clustering so the same story doesn't brief twice in a week
- [ ] optional per-niche gate configuration

MIT licensed. Built by [Assis Devassy](https://assisdevassy.netlify.app) —
marketing engineer building the machines that run modern GTM.
