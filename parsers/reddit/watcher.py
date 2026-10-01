#!/usr/bin/env python3

import json
import re
import time
import urllib.request
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"

USER_AGENT = "PoWEarlyWatch/1.0 (Reddit PoW monitoring)"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_subreddit(subreddit, limit):
    url = (
        f"https://www.reddit.com/r/{subreddit}/new.json"
        f"?limit={limit}&raw_json=1"
    )

    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT}
    )

    with urllib.request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def phrase_found(text, phrase):
    text = text.lower()
    phrase = phrase.lower()

    pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
    return re.search(pattern, text) is not None


def score_post(post, config):
    title = post.get("title", "")
    selftext = post.get("selftext", "")

    text = f"{title}\n{selftext}"

    score = 0
    matches = []

    for group in config["signals"]:
        weight = group["weight"]

        matched_phrases = []

        for phrase in group["phrases"]:
            if phrase_found(text, phrase):
                matched_phrases.append(phrase)

        if matched_phrases:
            score += weight

            # Показываем одну лучшую фразу из каждой группы
            matches.append({
                "weight": weight,
                "phrase": matched_phrases[0],
                "group": group["name"]
            })

    for group in config.get("negative_signals", []):
        weight = group["weight"]

        for phrase in group["phrases"]:
            if phrase_found(text, phrase):
                score += weight
                matches.append({
                    "weight": weight,
                    "phrase": phrase,
                    "group": "negative"
                })
                break

    return score, matches


def main():
    config = load_config()

    now = time.time()
    max_age = config["max_age_hours"] * 3600

    results = []

    print()
    print("=== Reddit Early PoW Watch ===")
    print(f"Порог: {config['score_threshold']}")
    print(f"Свежесть: {config['max_age_hours']} часов")
    print()

    for subreddit in config["subreddits"]:
        print(f"Проверяю r/{subreddit} ...")

        try:
            data = fetch_subreddit(
                subreddit,
                config["posts_per_subreddit"]
            )

            children = data["data"]["children"]

            for child in children:
                post = child["data"]

                created = post.get("created_utc", 0)
                age = now - created

                if age < 0 or age > max_age:
                    continue

                score, matches = score_post(post, config)

                if score < config["score_threshold"]:
                    continue

                permalink = post.get("permalink", "")

                results.append({
                    "title": post.get("title", ""),
                    "subreddit": post.get("subreddit", subreddit),
                    "score": score,
                    "matches": matches,
                    "url": "https://www.reddit.com" + permalink,
                    "created": created
                })

        except Exception as e:
            print(f"  ❌ Ошибка: {e}")

        # Не долбим Reddit запросами подряд
        time.sleep(1)

    results.sort(
        key=lambda x: x["created"],
        reverse=True
    )

    print()
    print("=" * 70)
    print(f"Найдено подходящих постов: {len(results)}")
    print("=" * 70)

    for item in results:
        signals = sorted(
            item["matches"],
            key=lambda x: x["weight"],
            reverse=True
        )

        signals = signals[:config["max_display_signals"]]

        signal_text = " | ".join(
            f"{s['weight']:+d} {s['phrase']}"
            for s in signals
        )

        print()
        print(f"🆕 Reddit — Score {item['score']}")
        print()
        print(item["title"])
        print()
        print(f"r/{item['subreddit']}")
        print(f"Сигналы: {signal_text}")
        print(f"🔗 {item['url']}")
        print("-" * 70)


if __name__ == "__main__":
    main()
