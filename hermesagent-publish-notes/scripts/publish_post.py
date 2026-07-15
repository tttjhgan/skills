#!/usr/bin/env python3
"""Validate and publish a standalone Markdown post through HermesAgent."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_ENDPOINT = "http://49.232.56.77:7800/api/publish"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True)
    content_source = parser.add_mutually_exclusive_group(required=True)
    content_source.add_argument("--content-file", type=Path)
    content_source.add_argument("--content")
    parser.add_argument("--tags", default="")
    parser.add_argument("--categories", default="随笔")
    parser.add_argument("--slug")
    parser.add_argument("--draft", action="store_true")
    parser.add_argument("--send", action="store_true")
    parser.add_argument("--endpoint", default=os.getenv("HERMESAGENT_PUBLISH_ENDPOINT", DEFAULT_ENDPOINT))
    parser.add_argument("--timeout", type=float, default=20)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.content_file and not args.content_file.is_file():
        print(f"error: content file not found: {args.content_file}", file=sys.stderr)
        return 2
    content = args.content if args.content is not None else args.content_file.read_text(encoding="utf-8")
    payload = {
        "title": args.title.strip(),
        "content": content.strip(),
        "tags": [item.strip() for item in args.tags.split(",") if item.strip()],
        "categories": [item.strip() for item in args.categories.split(",") if item.strip()],
        "draft": args.draft,
    }
    if args.slug:
        payload["slug"] = args.slug.strip()
    if not payload["title"] or not payload["content"]:
        print("error: title and content must be non-empty", file=sys.stderr)
        return 2
    if not args.send:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print("Preview only. Add --send to publish.", file=sys.stderr)
        return 0
    token = os.getenv("HERMESAGENT_NOTES_TOKEN")
    if not token:
        print("error: HERMESAGENT_NOTES_TOKEN is not set", file=sys.stderr)
        return 2
    request = urllib.request.Request(
        args.endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8", "Accept": "application/json, text/plain, */*", "Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            print(f"Published through HermesAgent: HTTP {response.status}")
            print(body)
            return 0
    except urllib.error.HTTPError as error:
        print(f"error: HermesAgent rejected the post: HTTP {error.code}", file=sys.stderr)
        print(error.read().decode("utf-8", errors="replace"), file=sys.stderr)
    except (urllib.error.URLError, TimeoutError) as error:
        print(f"error: could not reach HermesAgent: {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
