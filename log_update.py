import os
import datetime

log_dir = r"c:\Projects\GetMeAJob\.agent\logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "chat_history.md")

with open(log_file, "a", encoding="utf-8") as f:
    f.write(f"\n\n## [{datetime.datetime.now().isoformat()}]\n")
    f.write("**User Input**:\nWe need to narrow down the search to job only in USA\n\n")
    f.write("**Agent Reasoning**:\nThe user requested to restrict the job search geographically to the United States. I added a `SEARCH_LOCATION` variable to `config.py` and updated the `scout.py` payload to dynamically inject this location constraint instead of defaulting to 'Worldwide'.\n\n")
    f.write("**Actions Taken**:\n")
    f.write("- Added `SEARCH_LOCATION = 'United States'` to `config.py`.\n")
    f.write("- Modified `scout.py` to use `config.SEARCH_LOCATION` in the HTTP query parameters.\n")
    f.write("- Tracked changes in the task list.\n")
