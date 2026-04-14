# s3-finops-kit

> FinOps toolkit focused on AWS S3 — collect storage data, visualize costs on an interactive dashboard, and get AI-powered recommendations.

## What it does today

- Collects storage class data from all S3 buckets across multiple regions via CloudWatch
- Audits which buckets have lifecycle policies configured
- Exports data to CSV with timestamp for historical tracking
- Displays everything on a public interactive dashboard with charts, cards, filters, and lifecycle status per bucket

## Roadmap

### Collect
| Script | Description | Status |
|---|---|---|
| `report.py` | Collects storage class data per bucket via CloudWatch and exports to CSV | ✅ Done |
| `lifecycle_auditor.py` | Lists buckets without lifecycle policies configured | ✅ Done |
| `cost_explorer.py` | Fetches real billed cost per bucket from AWS Cost Explorer | 🔜 Next |
| `abandoned_bucket_detector.py` | Finds buckets with zero access in the last 90 days | 📋 Planned |
| `intelligent_tiering_evaluator.py` | Calculates break-even point for migrating to S3 Intelligent-Tiering | 📋 Planned |
| `replication_cost_tracker.py` | Tracks cross-region replication storage and transfer costs | 📋 Planned |

### Visualize
| Feature | Status |
|---|---|
| Dashboard with dark theme, cards, chart and filters | ✅ Done |
| Storage breakdown by storage class | ✅ Done |
| Lifecycle policy status per bucket | ✅ Done |
| Card showing buckets without lifecycle policy | ✅ Done |
| Real billed cost per bucket | 🔜 Next |
| Cost trend over time | 📋 Planned |
| FinOps health score per bucket (0–100) | 📋 Planned |

### Automate
| Feature | Status |
|---|---|
| Daily GitHub Actions scheduler | 📋 Planned |
| Auto-update dashboard data | 📋 Planned |
| Tag enforcer for untagged buckets | 📋 Planned |

### AI Advisor
| Feature | Status |
|---|---|
| Claude-powered natural language recommendations | 📋 Planned |
| "Why is this bucket expensive?" chat interface | 📋 Planned |
| Savings prioritization by impact | 📋 Planned |

## Project structure

```
s3-finops-kit/
├── report.py              # collects storage class data and exports to CSV
├── lifecycle_auditor.py   # audits lifecycle policies per bucket
├── data/
│   ├── data.csv           # latest storage data (read by dashboard)
│   ├── lifecycle.csv      # latest lifecycle audit (read by dashboard)
│   └── *_TIMESTAMP.csv    # historical snapshots
├── index.html             # public dashboard — GitHub Pages
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

```bash
git clone https://github.com/rendell-arruda/s3-finops-kit.git
cd s3-finops-kit
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in your AWS_PROFILE
python report.py
python lifecycle_auditor.py
```

## Requirements

- Python 3.12+
- AWS credentials configured (`~/.aws/credentials`)
- Permissions: `s3:ListAllMyBuckets`, `s3:GetBucketLocation`, `s3:GetBucketLifecycleConfiguration`, `cloudwatch:GetMetricStatistics`

## Dashboard

Published at: `https://rendell-arruda.github.io/s3-finops-kit`

## License

MIT