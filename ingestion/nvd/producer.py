from __future__ import annotations

import os

from ingestion.common import SourceContext, build_parser, run_source
from threatlake.settings import ThreatLakeSettings
from threatlake.sources.nvd import fetch_nvd


def main() -> None:
    parser = build_parser("Fetch NVD CVEs and publish raw records")
    args = parser.parse_args()
    settings = ThreatLakeSettings.from_env()
    ctx = SourceContext(
        settings=settings,
        source_name="nvd",
        topic_name=f"{settings.raw_topic_prefix}.nvd",
        fetcher=lambda cfg: fetch_nvd(
            cfg.nvd_api_url,
            timeout=cfg.api_timeout_seconds,
            api_key=os.getenv("NVD_API_KEY"),
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

