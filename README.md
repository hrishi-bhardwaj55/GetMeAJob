# Real-time Job Intelligence Agent

A Python-based, multi-agent system that autonomously scrapes LinkedIn for recent job openings, evaluates descriptions against your criteria, deduplicates findings, and sends live alerts directly to a Discord Webhook.

## Features
- **Scout Agent**: Uses headless Playwright browsers with randomized User-Agents to bypass basic bot-detection, scanning LinkedIn for jobs posted in the "Past 24 Hours".
- **Filter Agent**: Visits individual application pages, parses descriptions, and scores jobs based on `required`, `preferred`, and `excluded` keywords.
- **Database Engine**: Uses local SQLite (`jobs.db`) to ensure you never receive the same job alert twice.
- **Notifier Agent**: Dispatches rich, formatted Discord Embeds.

---

## 🚀 How to Use (The Easy Way - Docker)

The easiest way to run this on **any** computer (Windows, Mac, Linux) without worrying about installing Python, Playwright, or dependencies is to use Docker.

### Prerequisites
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. Create your [Discord Webhook URL](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks).

### Setup & Run
1. Open `config.py` in any text editor.
2. Update `SEARCH_KEYWORDS` with what you want to search for.
3. Update `DISCORD_WEBHOOK_URL` with your Discord link.
4. Open your terminal in this folder and build the container:
   ```bash
   docker build -t job-agent .
   ```
5. Run the container in the background:
   ```bash
   docker run -d --name my-job-agent -v $(pwd)/jobs.db:/app/jobs.db job-agent
   ```
*(Note: We mount the `jobs.db` file so your deduplication history is saved even if the container restarts).*

---

## 💻 How to Use (Local Python Setup)

If you prefer to run it directly on your machine instead of Docker:

1. Requires Python 3.10+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
3. Update your `config.py` variables.
4. Run the orchestration loop natively:
   ```bash
   python main.py
   ```

To do a single dry-run test without sending notifications or looping forever:
```bash
python main.py --dry-run
```