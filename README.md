# s3-finops-lens

> FinOps toolkit focused on AWS S3 — detect waste, visualize costs, and automate corrective actions with AI-powered recommendations.

## Features

### Detect
| Module | Description |
|---|---|
| `storage_class_analyzer` | Breaks down storage volume and estimated cost by storage class per bucket |
| `lifecycle_auditor` | Identifies buckets without lifecycle policies — a major source of unnecessary cost |
| `abandoned_bucket_detector` | Finds buckets with zero access in the last 90 days |
| `request_cost_estimator` | Estimates GET/PUT/LIST request costs via CloudWatch metrics |
| `intelligent_tiering_evaluator` | Calculates break-even point for migrating to S3 Intelligent-Tiering |
| `replication_cost_tracker` | Tracks cross-region replication storage and transfer costs |

### Visualize
Interactive dashboard published on GitHub Pages, updated daily via GitHub Actions.
- Cost overview per bucket and storage class
- Savings opportunities ranked by impact
- FinOps health score per bucket (0–100)
- Cost trend over time
- Drill-down per bucket

### Automate
- Daily GitHub Actions scheduler
- Cost anomaly alerter
- Lifecycle auto-applicator (with dry-run mode)
- Tag enforcer for untagged buckets

### AI Advisor
Claude-powered analysis of collected data — natural language recommendations, savings prioritization, and interactive chat over your S3 cost data.

## Project structure

```
s3-finops-lens/
├── collectors/             # boto3 data collection scripts
│   ├── storage_class_analyzer.py
│   ├── lifecycle_auditor.py
│   └── ...
├── exporters/              # JSON/CSV output formatters
│   └── json_exporter.py
├── advisors/               # AI recommendation engine
│   └── ai_advisor.py
├── dashboard/              # GitHub Pages static site
│   ├── index.html
│   ├── data/               # generated JSON files (updated by Actions)
│   ├── js/
│   └── css/
├── docs/                   # architecture and feature docs
├── .github/
│   └── workflows/
│       └── daily_analysis.yml
├── main.py                 # entrypoint — runs all collectors + exporter
├── requirements.txt
└── .env.example
```

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/s3-finops-lens.git
cd s3-finops-lens
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in your AWS_PROFILE and region
python main.py --dry-run
```

## Requirements

- Python 3.12+
- AWS credentials configured (`~/.aws/credentials` or environment variables)
- Permissions: `s3:ListAllMyBuckets`, `s3:GetBucketLifecycleConfiguration`, `cloudwatch:GetMetricStatistics`, `ce:GetCostAndUsage`

## Dashboard

Published at: `https://YOUR_USERNAME.github.io/s3-finops-lens`

Updated daily via GitHub Actions. Data lives in `dashboard/data/*.json`.

## License

MIT
