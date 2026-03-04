import os
import datetime

log_dir = r"c:\Projects\GetMeAJob\.agent\logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "chat_history.md")

with open(log_file, "a", encoding="utf-8") as f:
    f.write(f"\n\n## [{datetime.datetime.now().isoformat()}]\n")
    f.write("**Agent Reasoning**:\nI discovered that `test_notification.py` broke because it was still using the old monolithic `NotifierAgent()` constructor. I injected the new parameterized URL and bot name to fix it, and executed the payload. The webhook routed securely. I am now committing the entire Refactor to git.\n\n")
    f.write("**Actions Taken**:\n")
    f.write("- Fixed `test_notification.py` to pull dynamic bot arguments.\n")
    f.write("- Verified dynamic webhook delivery success.\n")
    f.write("- Committed codebase via `git commit`.\n")
