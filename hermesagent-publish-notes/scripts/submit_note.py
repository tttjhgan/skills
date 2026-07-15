#!/usr/bin/env python3
"""Validate and submit a Markdown note to HermesAgent's ingestion endpoint."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_ENDPOINT = "http://49.232.56.77:7800/api/notes"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True, help="Note title")
    parser.add_argument("--chapter", required=True, help="Target series chapter slug")
    content_source = parser.add_mutually_exclusive_group(required=True)
    content_source.add_argument("--content-file", type=Path, help="UTF-8 Markdown file")
    content_source.add_argument("--content", help="Markdown content")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--send", action="store_true", help="POST the note; omit to preview JSON")
    parser.add_argument("--endpoint", default=os.getenv("HERMESAGENT_NOTES_ENDPOINT", DEFAULT_ENDPOINT))
    parser.add_argument("--timeout", type=float, default=20, help="HTTP timeout in seconds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.content_file and not args.content_file.is_file():
        print(f"error: content file not found: {args.content_file}", file=sys.stderr)
        return 2

    content = args.content if args.content is not None else args.content_file.read_text(encoding="utf-8")
    content = content.strip()
    if not args.title.strip() or not args.chapter.strip() or not content:
        print("error: title, chapter, and Markdown content must be non-empty", file=sys.stderr)
        return 2

    payload = {
        "title": args.title.strip(),
        "chapter": args.chapter.strip(),
        "content": content,
        "tags": [tag.strip() for tag in args.tags.split(",") if tag.strip()],
    }
    encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    if not args.send:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print("Preview only. Add --send to submit.", file=sys.stderr)
        return 0

    token = os.getenv("HERMESAGENT_NOTES_TOKEN")
    if not token:
        print("error: HERMESAGENT_NOTES_TOKEN is not set", file=sys.stderr)
        return 2
    request = urllib.request.Request(
        args.endpoint,
        data=encoded,
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8", "Accept": "application/json, text/plain, */*", "Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            print(f"Accepted by HermesAgent: HTTP {response.status}")
            if body:
                print(body)
            return 0
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        print(f"error: HermesAgent rejected the note: HTTP {error.code}", file=sys.stderr)
        if body:
            print(body, file=sys.stderr)
    except (urllib.error.URLError, TimeoutError) as error:
        print(f"error: could not reach HermesAgent: {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
