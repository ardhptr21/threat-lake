from __future__ import annotations

import os

from ingestion.common import SourceContext, build_parser, run_source
from threatlake.settings import ThreatLakeSettings
from threatlake.sources.github_events import fetch_github_events


def main() -> None:
    parser = build_parser("Fetch GitHub events and publish raw records")
    args = parser.parse_args()
    settings = ThreatLakeSettings.from_env()
    ctx = SourceContext(
        settings=settings,
        source_name="github_events",
        topic_name=f"{settings.raw_topic_prefix}.github_events",
        fetcher=lambda cfg: fetch_github_events(
            cfg.github_events_url,
            timeout=cfg.api_timeout_seconds,
            token=os.getenv("GITHUB_TOKEN"),
        ),
    )
    run_source(
        ctx,
        once=args.once,
        interval=args.interval,
        write_local=args.write_local,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()

