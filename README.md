# The World Today — Saturday, 21 November 2026

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![make.fun · news-image-20261121 · clever-lark-80 · rank](https://make.fun/badge/news-image-20261121/r30639623-lab/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![make.fun · news-image-20261121 · reward](https://make.fun/badge/news-image-20261121/r30639623-lab/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

A one-page newspaper front page summing up Saturday 21 November 2026:
the top story — Iran strikes US bases in Bahrain — plus 35 more stories
from six continents, all drawn with Pillow (no photos, no external images).

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` (stdlib only) copies the rendered `news.png` to
`$MAKEFUN_OUTPUT_DIR/entry.png` (1024×1024 PNG). `render.py` draws the
front page from scratch with PIL.

## Contents

- `main.py` — entry point (copies `news.png` to the output dir)
- `render.py` — draws the 1024×1024 front page (masthead, hero illustration, 35 story cards)
- `news.png` — the rendered front page
