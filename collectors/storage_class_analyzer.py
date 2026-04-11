"""
collectors/storage_class_analyzer.py

Collects storage volume (in GB) and estimated monthly cost per storage class
for every S3 bucket in the account.

Data source: CloudWatch BucketSizeBytes metric (updated daily by AWS).
Pricing reference: https://aws.amazon.com/s3/pricing/ (sa-east-1 defaults)
"""

import os
import boto3
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# S3 storage class pricing — USD per GB/month (sa-east-1)
# Source: https://aws.amazon.com/s3/pricing/
# Update these values if your primary region differs.
# ---------------------------------------------------------------------------
PRICING_PER_GB: dict[str, float] = {
    "StandardStorage":            0.0245,
    "IntelligentTieringStorage":  0.0245,  # frequent access tier
    "StandardIAStorage":          0.0138,
    "OneZoneIAStorage":           0.011,
    "GlacierInstantStorage":      0.005,
    "GlacierStorage":             0.0045,
    "DeepArchiveStorage":         0.0018,
}

STORAGE_CLASS_LABELS: dict[str, str] = {
    "StandardStorage":            "S3 Standard",
    "IntelligentTieringStorage":  "Intelligent-Tiering",
    "StandardIAStorage":          "Standard-IA",
    "OneZoneIAStorage":           "One Zone-IA",
    "GlacierInstantStorage":      "Glacier Instant Retrieval",
    "GlacierStorage":             "Glacier Flexible Retrieval",
    "DeepArchiveStorage":         "Glacier Deep Archive",
}

BYTES_IN_GB = 1024 ** 3


def _get_bucket_size_gb(
    cw_client,
    bucket_name: str,
    storage_type: str,
) -> float:
    """Query CloudWatch for BucketSizeBytes and return size in GB."""
    end = datetime.now(tz=timezone.utc)
    start = end - timedelta(days=2)  # AWS updates this metric daily

    response = cw_client.get_metric_statistics(
        Namespace="AWS/S3",
        MetricName="BucketSizeBytes",
        Dimensions=[
            {"Name": "BucketName", "Value": bucket_name},
            {"Name": "StorageType", "Value": storage_type},
        ],
        StartTime=start,
        EndTime=end,
        Period=86400,  # 1 day
        Statistics=["Average"],
    )

    datapoints = response.get("Datapoints", [])
    if not datapoints:
        return 0.0

    latest = max(datapoints, key=lambda d: d["Timestamp"])
    return latest["Average"] / BYTES_IN_GB


def collect(region: str | None = None) -> list[dict]:
    """
    Collect storage class breakdown for all buckets.

    Returns a list of dicts, one per (bucket, storage_class) combination
    that has non-zero storage.

    Each dict contains:
        bucket_name       str
        region            str
        storage_class_key str   (CloudWatch StorageType key)
        storage_class     str   (human-readable label)
        size_gb           float
        estimated_cost_usd float (monthly estimate)
        collected_at      str   (ISO 8601 UTC)
    """
    aws_region = region or os.getenv("AWS_REGION", "sa-east-1")
    aws_profile = os.getenv("AWS_PROFILE")

    session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
    s3 = session.client("s3")
    cw = session.client("cloudwatch", region_name=aws_region)

    collected_at = datetime.now(tz=timezone.utc).isoformat()

    buckets_response = s3.list_buckets()
    buckets = buckets_response.get("Buckets", [])

    results: list[dict] = []

    for bucket in buckets:
        bucket_name = bucket["Name"]
        print(f"  Analyzing: {bucket_name}")

        for storage_key, label in STORAGE_CLASS_LABELS.items():
            size_gb = _get_bucket_size_gb(cw, bucket_name, storage_key)

            if size_gb == 0.0:
                continue

            price_per_gb = PRICING_PER_GB.get(storage_key, 0.0)
            estimated_cost = round(size_gb * price_per_gb, 4)

            results.append({
                "bucket_name": bucket_name,
                "region": aws_region,
                "storage_class_key": storage_key,
                "storage_class": label,
                "size_gb": round(size_gb, 4),
                "estimated_cost_usd": estimated_cost,
                "collected_at": collected_at,
            })

    return results


if __name__ == "__main__":
    print("Running storage class analyzer...")
    data = collect()
    print(f"\nFound {len(data)} storage class entries across all buckets.\n")
    for entry in data:
        print(
            f"  {entry['bucket_name']} | {entry['storage_class']} | "
            f"{entry['size_gb']:.2f} GB | ${entry['estimated_cost_usd']:.4f}/mo"
        )
