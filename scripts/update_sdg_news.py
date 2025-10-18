#!/usr/bin/env python3
"""Generate SDG-focused social posts for the AZMIU website widget.

The script aggregates Sustainable Development Goals (SDG) news from
international university sources, blends it with local AZMIU research
highlights, and produces structured content consumable by the front-end
widget. Designed to be run on a daily schedule (e.g. cron).
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import json
import random
import textwrap
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from typing import Iterable, List, Optional

# --- Configuration -------------------------------------------------------

RSS_FEEDS: List[tuple[str, str]] = [
    (
        "Times Higher Education SDG Impact",
        "https://www.timeshighereducation.com/rss/sdg",
    ),
    (
        "University World News SDGs",
        "https://www.universityworldnews.com/rss/section.php?ct=sdg",
    ),
    (
        "UN SDG Action",
        "https://sdgactioncampaign.org/feed/",
    ),
]

KEYWORDS = [
    "university",
    "campus",
    "students",
    "research",
    "sustainability",
    "climate",
    "energy",
    "education",
]

LOCAL_DATA_PATH = "data/local_highlights.json"
AZMIU_UPDATES_PATH = "data/azmiu_updates.json"
GLOBAL_FALLBACK_PATH = "data/global_highlights.json"
OUTPUT_PATH = "data/sdg_stream.json"
MAX_GLOBAL_ITEMS = 6
MAX_AZMIU_ITEMS = 6

DEFAULT_HASHTAGS = ["#SDGs", "#AZMIU", "#UniversityImpact"]

# --- Data structures -----------------------------------------------------


@dataclasses.dataclass
class FeedItem:
    title: str
    link: str
    published: Optional[dt.datetime]
    summary: str
    source: str


@dataclasses.dataclass
class SocialPost:
    text: str
    link: str
    published: str
    source: str
    hashtags: list[str]


# --- Fetching helpers ----------------------------------------------------


def fetch_feed(url: str, source: str) -> Iterable[FeedItem]:
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            raw = response.read()
    except urllib.error.URLError as exc:
        print(f"Failed to fetch {url}: {exc}")
        return []

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        print(f"Failed to parse feed from {url}: {exc}")
        return []

    channel = root.find("channel")
    if channel is None:
        # Atom feeds do not necessarily have a channel element; fall back to entries
        entries = root.findall(".//entry")
        for entry in entries:
            title = entry.findtext("title", default="")
            link_el = entry.find("link")
            link = link_el.attrib.get("href", "") if link_el is not None else ""
            published_text = entry.findtext("updated") or entry.findtext("published")
            summary = entry.findtext("summary") or entry.findtext("content") or ""
            yield FeedItem(
                title=title.strip(),
                link=link.strip(),
                published=parse_date(published_text),
                summary=clean_text(summary),
                source=source,
            )
        return

    for item in channel.findall("item"):
        title = item.findtext("title", default="").strip()
        link = item.findtext("link", default="").strip()
        summary = item.findtext("description", default="")
        published_text = item.findtext("pubDate")
        yield FeedItem(
            title=title,
            link=link,
            published=parse_date(published_text),
            summary=clean_text(summary),
            source=source,
        )


def parse_date(raw: Optional[str]) -> Optional[dt.datetime]:
    if not raw:
        return None
    raw = raw.strip()
    try:
        normalized = raw.replace("Z", "+00:00") if raw.endswith("Z") else raw
        return dt.datetime.fromisoformat(normalized)
    except ValueError:
        pass
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
    ):
        try:
            return dt.datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def clean_text(raw: str) -> str:
    text = ET.fromstring(f"<div>{raw}</div>").itertext()
    joined = " ".join(fragment.strip() for fragment in text)
    return " ".join(joined.split())


def filter_items(items: Iterable[FeedItem]) -> list[FeedItem]:
    filtered: list[FeedItem] = []
    for item in items:
        haystack = f"{item.title.lower()} {item.summary.lower()}"
        if any(keyword in haystack for keyword in KEYWORDS):
            filtered.append(item)
    return filtered


# --- Local data integration ---------------------------------------------


def load_local_highlights(path: str) -> list[dict]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as exc:
        print(f"Failed to parse local highlights {path}: {exc}")
        return []
    return data


def load_json_records(path: str) -> list[dict]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as exc:
        print(f"Failed to parse JSON from {path}: {exc}")
        return []


def load_global_fallbacks(path: str) -> list[FeedItem]:
    records = load_json_records(path)
    fallbacks: list[FeedItem] = []
    for record in records:
        fallbacks.append(
            FeedItem(
                title=record.get("title", ""),
                link=record.get("link", ""),
                published=parse_date(record.get("published")),
                summary=record.get("summary", ""),
                source=record.get("source", "Official SDG News"),
            )
        )
    return fallbacks


def craft_global_post(item: FeedItem, local_focus: dict) -> SocialPost:
    published = item.published or dt.datetime.utcnow()
    summary = textwrap.shorten(item.summary, width=160, placeholder="…")
    local_blurb = local_focus.get("summary", "Discover AZMIU's sustainable development efforts.")
    hashtags = sorted(set(DEFAULT_HASHTAGS + local_focus.get("hashtags", [])))

    text = (
        f"{item.title} — {summary} "
        f"AZMIU connection: {local_focus.get('title', 'Explore our SDG work')}. "
        f"{local_blurb}"
    )

    return SocialPost(
        text=text,
        link=item.link or local_focus.get("url", ""),
        published=published.isoformat(),
        source=item.source,
        hashtags=hashtags,
    )


def craft_azmiu_post(record: dict) -> SocialPost:
    published = parse_date(record.get("published")) or dt.datetime.utcnow()
    text = (
        f"{record.get('title', 'AZMIU SDG achievement')} — "
        f"{record.get('summary', '').strip()}"
    ).strip()
    link = record.get("url", "")
    source = record.get("source", "AZMIU Newsroom")
    hashtags = sorted(set(DEFAULT_HASHTAGS + record.get("hashtags", [])))

    return SocialPost(
        text=text,
        link=link,
        published=published.isoformat(),
        source=source,
        hashtags=hashtags,
    )


# --- Main orchestration --------------------------------------------------


def generate_posts() -> tuple[list[SocialPost], list[SocialPost]]:
    all_items: list[FeedItem] = []
    for source, url in RSS_FEEDS:
        feed_items = list(fetch_feed(url, source))
        all_items.extend(feed_items)

    all_items = filter_items(all_items)
    all_items.sort(key=lambda item: item.published or dt.datetime.utcnow(), reverse=True)
    all_items = all_items[: MAX_GLOBAL_ITEMS * 2]

    local_highlights = load_local_highlights(LOCAL_DATA_PATH)
    if not local_highlights:
        local_highlights = [
            {
                "title": "AZMIU research spotlight",
                "url": "https://sdg.azmiu.edu.az/research",
                "summary": "Explore the latest Sustainable Development research from AZMIU faculty and students.",
                "hashtags": ["#AZMIUResearch"],
            }
        ]

    if not all_items:
        all_items = load_global_fallbacks(GLOBAL_FALLBACK_PATH)

    global_posts: list[SocialPost] = []
    for item in all_items[:MAX_GLOBAL_ITEMS]:
        local_focus = random.choice(local_highlights)
        global_posts.append(craft_global_post(item, local_focus))

    azmiu_records = load_json_records(AZMIU_UPDATES_PATH)
    azmiu_posts: list[SocialPost] = []
    for record in azmiu_records[:MAX_AZMIU_ITEMS]:
        azmiu_posts.append(craft_azmiu_post(record))

    if not azmiu_posts:
        fallback_hashtags = sorted(set(DEFAULT_HASHTAGS))
        now = dt.datetime.utcnow().isoformat()
        for highlight in local_highlights:
            text = (
                f"AZMIU Spotlight — {highlight.get('title', 'SDG innovation')} "
                f"{highlight.get('summary', '')}"
            )
            azmiu_posts.append(
                SocialPost(
                    text=text.strip(),
                    link=highlight.get("url", ""),
                    published=now,
                    source="AZMIU Research",
                    hashtags=sorted(set(fallback_hashtags + highlight.get("hashtags", []))),
                )
            )

    return global_posts, azmiu_posts


def save_posts(global_posts: Iterable[SocialPost], azmiu_posts: Iterable[SocialPost], path: str) -> None:
    payload = {
        "generated_at": dt.datetime.utcnow().isoformat(),
        "global_posts": [dataclasses.asdict(post) for post in global_posts],
        "azmiu_posts": [dataclasses.asdict(post) for post in azmiu_posts],
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)


def main() -> None:
    global_posts, azmiu_posts = generate_posts()
    save_posts(global_posts, azmiu_posts, OUTPUT_PATH)
    print(
        "Generated "
        f"{len(global_posts)} global SDG stories and {len(azmiu_posts)} AZMIU updates for the website widget."
    )


if __name__ == "__main__":
    main()
