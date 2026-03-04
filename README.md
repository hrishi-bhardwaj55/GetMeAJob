# GetMeAJob 🤖

A Python-based, multi-agent system that autonomously scrapes LinkedIn for recent job openings, evaluates descriptions against your criteria, deduplicates findings, and sends live alerts directly to Discord — through separate, specialized bots.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Multi-Bot Architecture** | Run separate bots for different role categories (SWE, Data, AI/ML), each with its own Discord channel |
| **Smart Filtering** | Scores jobs against required skills, preferred skills, and excluded terms |
| **Rich Discord Embeds** | Each notification shows salary, skills detected, experience required, and post time |
| **No Duplicates** | SQLite database ensures you never receive the same job alert twice |
| **Full-Time Only** | Automatically filters out part-time, contract, intern, and security-clearance-only roles |
| **US Only** | Geo-locked to United States results using LinkedIn's internal geoId |
| **Concurrent** | All bots run in parallel; description fetching uses 5 concurrent workers per bot |

---

## 🚀 Setup (Local Python)

**Requirements:** Python 3.10+

```bash
# 1. Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\activate          # Windows
source venv/bin/activate         # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt
playwright install chromium
```

---

## ⚙️ Configuration (`config.py`)

Open `config.py` to configure your bots. Each profile in `JOB_PROFILES` is independent:

```python
JOB_PROFILES = [
    {
        "name": "Software Engineering Bot",
        "tag": "sde",                        # Used with --bots flag
        "keywords": ["Software Engineer", "Senior Software Engineer"],
        "location": "United States",
        "webhook_url": "YOUR_DISCORD_WEBHOOK_URL_HERE",
        "criteria": {
            "required_skills": [],           # Must appear in description or job is rejected
            "preferred_skills": [],          # Boost score if found
            "excluded_terms": [...],         # Any matching term = instant reject
            # "threshold": 80.0             # Optional: minimum score % to pass (default 80)
        }
    },
    ...
]
```

**To add a new bot:** Copy any profile block, give it a new `tag`, `name`, `keywords`, and `webhook_url`.

**Discord Webhook URL:** Create one in your Discord server under `Server Settings → Integrations → Webhooks`.

---

## ▶️ Running the Agent

### Run All Bots (auto-repeats every 60 min)
```bash
python main.py
```

### Run Once (manual trigger)
```bash
python main.py --run-once
```

### Run Specific Bots Only
Use the `--bots` flag with comma-separated tags from `config.py`:
```bash
# AI/ML bot only
python main.py --run-once --bots ai

# SWE + Data bots
python main.py --run-once --bots sde,data

# All bots explicitly
python main.py --run-once --bots sde,data,ai
```

### Dry Run (no Discord notifications sent)
```bash
python main.py --dry-run
```

### Test Your Webhook
Sends a sample notification to verify your Discord webhook is working:
```bash
python test_notification.py
```

### Reset the Database (re-send all jobs)
```bash
# Windows
Remove-Item jobs.db

# Mac/Linux
rm jobs.db
```

---

## 🐳 Docker Setup

```bash
# Build the image
docker build -t getmeajob .

# Run in background (persists the database)
docker run -d --name job-agent \
  -e SWE_WEBHOOK_URL="your_webhook_here" \
  -e DATA_WEBHOOK_URL="your_webhook_here" \
  -e AI_WEBHOOK_URL="your_webhook_here" \
  -v $(pwd)/jobs.db:/app/jobs.db \
  getmeajob
```

> **Tip:** Use environment variables (`SWE_WEBHOOK_URL`, `DATA_WEBHOOK_URL`, `AI_WEBHOOK_URL`) instead of hardcoding webhook URLs in `config.py`.

---

## 📁 Project Structure

```
GetMeAJob/
├── main.py          # Orchestrator — runs all bots, handles scheduling
├── config.py        # All configuration: bots, webhooks, keywords, criteria
├── scout.py         # Scout Agent — scrapes LinkedIn job cards
├── filter.py        # Filter Agent — fetches descriptions, scores jobs
├── notifier.py      # Notifier Agent — formats and sends Discord embeds
├── job_parser.py    # Parsers for salary, experience, and tech skills
├── database.py      # SQLite deduplication engine
├── test_notification.py  # Webhook delivery test
└── jobs.db          # Auto-created: tracks all processed job IDs
```

---

## 🔔 Discord Embed Format

Each notification includes:

| Field | Example |
|---|---|
| 📍 Location | New York, NY (Remote) |
| 💰 Salary | $130,000 - $180,000 |
| 🕐 Posted | 32 minutes ago |
| 🗓 Experience | 5+ years of experience |
| 🛠 Skills Detected | `Python` `AWS` `Docker` `Kubernetes` |
| 📄 Description | First 300 characters of the full JD |

---

## 🔧 Tuning Tips

- **Too many irrelevant jobs?** Add terms to `excluded_terms` in `config.py`.
- **Missing good jobs?** Lower the `threshold` (default 80%) or reduce `required_skills`.
- **Want fresher jobs?** The search window is currently 1 hour (`r3600`). Change `f_TPR` in `scout.py`.
- **Change poll frequency?** Edit `POLLING_INTERVAL_MINUTES` in `config.py`.