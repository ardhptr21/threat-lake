from __future__ import annotations

from ingestion.common import SourceContext, build_parser, run_source
from threatlake.settings import ThreatLakeSettings
from threatlake.sources.cisa import fetch_kev


def main() -> None:
    parser = build_parser("Fetch CISA KEV and publish raw records")
    args = parser.parse_args()
    settings = ThreatLakeSettings.from_env()
    ctx = SourceContext(
        settings=settings,
        source_name="cisa_kev",
        topic_name=f"{settings.raw_topic_prefix}.cisa_kev",
        fetcher=lambda cfg: fetch_kev(cfg.kev_feed_url, timeout=cfg.api_timeout_seconds),
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

