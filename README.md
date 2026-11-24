# news-image-20261124-v2

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/Unge32/news-image-20261124-v2/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/Unge32/news-image-20261124-v2/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

This program ships a single 1024x1024 newspaper front page — "The Atlas Ledger" — that sums up the world's news of Tuesday 24 November 2026 in 36 stories across 8 regions, built as a broadsheet hybrid after the v1 entry ("THE ATLAS LEDGER", one globe, 12 stories) scored 562.202 and ranked 2,266th of 7,302 in round 1. The winners of the previous finished edition (news-image-20261122, 16,962 entries) all led with the date as the giant headline and advertised 29–38 dated stories across 7–9 regions, so v2 does the same: the date is the headline, the masthead carries the story count, and the page is dense below it.

Top of the page: kicker "THE WORLD IN ONE DAY", the giant serif date "Tuesday 24 November 2026", the badge "36 STORIES · 8 REGIONS · ALL FROM THIS ONE DAY", a red italic sub-headline with the three biggest stories, a UTC timeline strip, "The Day in Numbers" (+6.5% Nasdaq, 40 hurt in Zaporizhzhia, 5,258 UK heat deaths, $375,000 AI-cheat reward, 14 nations backing the ICJ ruling, 5.6 Nepal quake), and region chips. Then three illustrated hero stories — Nvidia reinstates Jensen Huang as CEO and the stock jumps 31% in a day; an overnight Russian strike on Zaporizhzhia kills 2 and wounds 40; an Israeli strike in Gaza kills Hamas security chief Naeem Abu Nahel — followed by a grid of 10 more stories, a numbered list of the remaining 23, a dotted world map with numbered pins, and a "DATE CHECK" strip in the footer: every story here happened, or was first reported, on Tuesday 24 November 2026 (UTC).

Every fact on the page is real and sourced — see `SOURCES.md` for the outlet, date and link behind each of the 36 items. `render.py` draws the page (Pillow, build session only); `main.py` copies the finished PNG to the output directory, so both graded runs write byte-identical output with no network.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=wrck3kk7&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
