import os
import datetime

log_dir = r"c:\Projects\GetMeAJob\.agent\logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "chat_history.md")

with open(log_file, "a", encoding="utf-8") as f:
    f.write(f"\n\n## [{datetime.datetime.now().isoformat()}]\n")
    f.write("**User Input**:\ni received nothing for AI ML\n\n")
    f.write("**Agent Reasoning**:\nThe AI bot's criteria required 'Python' and preferred 'LLMs', 'Agentic', and 'Prompt Engineering'. By default, the `FilterAgent` demanded an 80% match score to pass a job. Earning just 'Python' and 'LLMs' scored a 60% (3 out of 5 points), causing the system to silently reject almost all real-world AI postings. I updated the FilterAgent to retrieve a custom `threshold` parameter directly from the config profile, and explicitly lowered the AI Bot's threshold to 40%.\n\n")
    f.write("**Actions Taken**:\n")
    f.write("- Updated `filter_jobs()` in `filter.py` to allow a profile-specific threshold.\n")
    f.write("- Bound the AI/ML Bot to a 40.0% threshold in `config.py`.\n")
    f.write("- Committed the bug fix resolving strict filtering bottlenecks.\n")
