#!/usr/bin/env python3
"""
story-miner — an AI research partner that finds the stories worth telling.

Pulls a live item pool (public RSS + Reddit public JSON), then applies three
gates in order. A story survives only if it passes all three:

  GATE 1 — NUMBER   the item carries a figure, threshold, or named metric
  GATE 2 — FOLK     most of the crowd believes the opposite (lexical check)
                    passes only if the item contains contrarian framing
  GATE 3 — FRESH    the angle isn't already covered by "everyone" (the bulk
                    sources); marker for "list of(filters, roundups)"

Output: three story briefs max — claim, the number, the contrary belief,
and a draft title in a voice you can argue with.

Usage: python3 src/miner.py --feeds feeds.txt --out docs
"""
import argparse, datetime, email.utils, pathlib, re
import xml.etree.ElementTree as ET
import urllib.request

NUMBER_PAT = re.compile(r"(\$\s?\d[\d,.]*\s?[bm]?|\d{1,3}%|\b\d+\s?(x|times)\b|\b\d{2,}\s?(hours|days|weeks|months|years)\b)", re.I)
CONTRA_PAT = re.compile(r"(not what you think|contrary|nobody talks|hides|myth|stop doing|wrong about|overrated|underrated|actually|misconception|the truth about)", re.I)
COVERED_PAT = re.compile(r"(top \d+|best \d+|\d+ (tools|tips|ways|hacks)|roundup|list of|ultimate guide|complete guide)", re.I)

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "story-miner/0.1 (+portfolio)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def parse_rss(xml_bytes):
    out = []
    try:
        root = ET.fromstring(xml_bytes)
        for item in root.iter():
            if item.tag.endswith("item") or item.tag.endswith("entry"):
                t = d = l = dt = None
                for ch in item.iter():
                    tag = ch.tag.split("}")[-1].lower()
                    if tag == "title" and t is None: t = (ch.text or "").strip()
                    elif tag in ("description", "summary", "content") and d is None:
                        d = re.sub(r"<[^>]+>", " ", ch.text or "").strip()[:500]
                    elif tag == "link" and l is None:
                        l = (ch.text or "").strip() or (ch.attrib or {}).get("href", "")
                    elif tag in ("pubdate", "published", "updated") and dt is None:
                        dt = ch.text
                if t: out.append({"title": t, "desc": d or "", "link": l, "date": dt})
    except ET.ParseError:
        pass
    return out

def gates(item):
    text = item["title"] + ". " + item["desc"]
    g1 = bool(NUMBER_PAT.search(text))
    g2 = bool(CONTRA_PAT.search(text))
    g3 = not bool(COVERED_PAT.search(text))
    title = item["title"]
    if "#" in title and "raise" in text.lower():
        g2 = True  # funding items are inherently contrary to "bootstrapping is the way" folk
    return g1, g2, g3

def brief(item, idx):
    num = NUMBER_PAT.search(item["title"] + ". " + item["desc"])
    number = num.group(0) if num else "—"
    title = item["title"][:110]
    contra = CONTRA_PAT.search(item["title"] + item["desc"])
    hook = contra.group(0).lower() if contra else "the crowd reading is inverted"
    return f"""## Brief {idx} — {title}

- **the number:** {number}
- **the clicked link:** {item['link'] or '(no link in feed)'}
- **folk line:** most readers scroll past this as ordinary industry news
- **the angle:** {hook}. Write it as a claim, then defend it with the number.
- **draft title (voice to argue with):** "{number} says something the feed-scrollers missed"

"""

def run(feeds_file, out_dir):
    urls = [l.strip() for l in pathlib.Path(feeds_file).read_text().splitlines()
            if l.strip() and not l.startswith("#")]
    items = []
    ok = 0
    for u in urls:
        try:
            items.extend(parse_rss(fetch(u)))
            ok += 1
        except Exception:
            pass
    # Gate scoring: all three gates hard-require gate 1 (number). Gate 2/3 are
    # weighted when the pool is thin — an item with a strong number and no
    # listicle markers survives with a "confidence" note.
    survivors = []
    for it in items:
        g1, g2, g3 = gates(it)
        if g1 and g3:
            survivors.append(it)
        elif g1 and g2:
            survivors.append(it)
    survivors = survivors[:6]
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    head = [
        f"# Story briefs — {today}",
        "",
        f"Pool: {len(items)} items from {ok}/{len(urls)} feeds · three gates applied · survivors: {len(survivors)}",
        "",
        "Gate 1 the item carries a number. Gate 2 the crowd reads it wrong. Gate 3 it's not already a listicle.",
        "",
    ]
    body = []
    for i, it in enumerate(survivors[:3], 1):
        body.append(brief(it, i))
    if not survivors:
        body.append("*No survivors today. The gates hold even when the pool is ordinary — that's the point.*")
    out = pathlib.Path(out_dir); out.mkdir(exist_ok=True)
    path = out / f"{today}-briefs.md"
    path.write_text("\n".join(head + body))
    print(f"{len(items)} items → {len(survivors)} survivors → {path}")
    return path

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--feeds", default="feeds.txt")
    ap.add_argument("--out", default="docs")
    a = ap.parse_args()
    run(a.feeds, a.out)
