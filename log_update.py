import os
import datetime

log_dir = r"c:\Projects\GetMeAJob\.agent\logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "chat_history.md")

with open(log_file, "a", encoding="utf-8") as f:
    f.write(f"\n\n## [{datetime.datetime.now().isoformat()}]\n")
    f.write("**User Input**:\nbut i am still not getting anything on my ai webhook. plus the jobs repeated from the last time we ran. they should not repeat. and I am getting jobs from canada brazil etc fix that\n\n")
    f.write("**Agent Reasoning**:\nI investigated three separate issues:\n")
    f.write("1. **Discord Rate Limits (Repeating Jobs & Missed Webhooks)**: The system was sending so many webhooks at once that Discord returned a 429 Rate Limit error. Because it threw a 429, `notifier.py` returned False. Consequently, `main.py` skipped the `db.mark_job_processed()` step for those jobs. The next time the loop ran, it saw them as unseen and tried (and failed) again. I fixed this by passing `rate_limit_retry=True` to the `DiscordWebhook` connection block, causing the bot to automatically sleep and retry instead of dropping the payload.\n")
    f.write("2. **Canada/Brazil Locations**: LinkedIn's URL parser is notoriously unreliable with text-based locations when no `geoId` is provided. I added a condition in `scout.py` to inject `geoId=103644278` (United States) directly into the scraping URL matrix tightly binding the queries to the USA.\n\n")
    f.write("**Actions Taken**:\n")
    f.write("- Enabled `rate_limit_retry=True` in `notifier.py`.\n")
    f.write("- Hardcoded `geoId=103644278` for 'United States' location queries in `scout.py`.\n")
