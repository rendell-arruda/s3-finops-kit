"""
main.py

Entrypoint for s3-finops-lens.
Runs all enabled collectors and exports results to dashboard/data/.

Usage:
    python main.py
    python main.py --dry-run     # prints output, skips file write
    python main.py --collector storage_class_analyzer
"""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from collectors import storage_class_analyzer

OUTPUT_DIR = Path("dashboard/data")


def run(dry_run: bool = False, collector: str | None = None) -> None:
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results: dict = {"generated_at": timestamp, "collectors": {}}

    collectors_to_run = {
        "storage_class_analyzer": storage_class_analyzer,
        # future collectors will be added here
    }

    if collector:
        collectors_to_run = {
            k: v for k, v in collectors_to_run.items() if k == collector
        }

    for name, module in collectors_to_run.items():
        print(f"\n[{name}] collecting...")
        data = module.collect()
        results["collectors"][name] = data
        print(f"[{name}] done — {len(data)} records")

    if dry_run:
        print("\n--- DRY RUN OUTPUT ---")
        print(json.dumps(results, indent=2))
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "analysis.json"
    output_path.write_text(json.dumps(results, indent=2))
    print(f"\nOutput written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="s3-finops-lens analysis runner")
    parser.add_argument("--dry-run", action="store_true", help="Print output, skip file write")
    parser.add_argument("--collector", type=str, help="Run a single collector by name")
    args = parser.parse_args()

    run(dry_run=args.dry_run, collector=args.collector)
