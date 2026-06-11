from __future__ import annotations

import os

from ingestion.common import SourceContext, build_parser, run_source
from threatlake.settings import ThreatLakeSettings
from threatlake.sources.github_advisory import fetch_github_advisories


def main() -> None:
    parser = build_parser("Fetch GitHub Security Advisories and publish raw records")
    args = parser.parse_args()
    settings = ThreatLakeSettings.from_env()
    ctx = SourceContext(
        settings=settings,
        source_name="github_advisory",
        topic_name=f"{settings.raw_topic_prefix}.github_advisory",
        fetcher=lambda cfg: fetch_github_advisories(
            cfg.github_advisory_url,
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

