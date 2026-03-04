import os
import datetime

log_dir = r"c:\Projects\GetMeAJob\.agent\logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "chat_history.md")

with open(log_file, "a", encoding="utf-8") as f:
    f.write(f"\n\n## [{datetime.datetime.now().isoformat()}]\n")
    f.write("**User Input**:\nI need to modify the time. only show job posted within the last two hours. and there are many irrelevant jobs also. Legal assistant etc. i am only looking for full time roles. remove any which have part time or contract or fixed duration mentioned. and don't repeat the jobs.\n\n")
    f.write("**Agent Reasoning**:\nThe user wanted stricter scraping (last 2 hours, full-time only). I updated `scout.py` payload constraints (`f_TPR=r7200` and `f_JT=F`). To filter out noise like 'Legal assistant' or 'contract', I globally populated the `excluded_terms` array in `config.py` for every bot profile. Repetitions are already prevented natively via `jobs.db`.\n\n")
    f.write("**Actions Taken**:\n")
    f.write("- Modified `scout.py` to enforce `f_TPR=r7200` (2 hours).\n")
    f.write("- Modified `scout.py` to enforce `f_JT=F` (Full-time only).\n")
    f.write("- Added `['part time', 'contract', 'assistant', 'legal'...]` to all `JOB_PROFILES` excluded terms.\n")
