from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import List

from .config import load_config
from .crawler import Crawler
from .http import HttpClient
from .parsers.aerolopa import AerolopaParser
from .storage import Storage
from .throttle import Throttle


def _read_urls_from_file(path: Path) -> List[str]:
    with path.open("r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="aerolopa-crawler",
        description="Fetch pages, parse content, normalize, and persist results.",
    )
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--urls-file", type=Path, help="Path to a text file with one URL per line")
    src.add_argument("--url", action="append", help="Specify one or more URLs (can repeat)")

    p.add_argument("--delay", type=float, help="Politeness delay between requests (seconds)")
    p.add_argument("--timeout", type=float, help="HTTP timeout in seconds")
    p.add_argument("--retries", type=int, help="Retry count on transient errors")
    p.add_argument("--user-agent", type=str, help="Custom User-Agent header")
    p.add_argument("--output-dir", type=Path, help="Directory for output files")
    p.add_argument("--verbose", "-v", action="count", default=0, help="Increase log verbosity")
    return p


def main(argv: List[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    # Logging config: default INFO, -v for DEBUG
    level = logging.DEBUG if args.verbose > 0 else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")
    log = logging.getLogger("aerolopa")

    cfg = load_config()

    # Override from CLI when provided
    if args.delay is not None:
        cfg.delay = args.delay
    if args.timeout is not None:
        cfg.timeout = args.timeout
    if args.retries is not None:
        cfg.retries = args.retries
    if args.user_agent is not None:
        cfg.user_agent = args.user_agent
    if args.output_dir is not None:
        cfg.output_dir = str(args.output_dir)

    # Resolve URLs
    urls: List[str]
    if args.urls_file:
        urls = _read_urls_from_file(args.urls_file)
    else:
        urls = list(args.url or [])

    if not urls:
        log.error("No URLs provided")
        return 2

    http = HttpClient(timeout=cfg.timeout, retries=cfg.retries, user_agent=cfg.user_agent)
    throttle = Throttle(delay=cfg.delay)
    storage = Storage(output_dir=cfg.output_dir)
    parser_impl = AerolopaParser()

    crawler = Crawler(client=http, parser=parser_impl, storage=storage, throttle=throttle, logger=log)
    processed = crawler.run(urls)
    log.info("Processed %d/%d URLs -> %s", processed, len(urls), storage.path)
    return 0 if processed > 0 else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

