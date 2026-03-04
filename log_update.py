import os
import datetime

log_dir = r"c:\Projects\GetMeAJob\.agent\logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "chat_history.md")

with open(log_file, "a", encoding="utf-8") as f:
    f.write(f"\n\n## [{datetime.datetime.now().isoformat()}]\n")
    f.write("**User Input**:\ncan i package in a way so that anyone can use it?\n\n")
    f.write("**Agent Reasoning**:\nThe built-in Playwright browsers can be tricky for non-developers to install across Windows/Mac/Linux. ")
    f.write("I chose to package the application using a Dockerfile referencing the official mcr.microsoft.com/playwright Python image. I also generated a requirements.txt and a README.md explaining both Docker and native setups.\n\n")
    f.write("**Actions Taken**:\n")
    f.write("- Piped pip freeze into requirements.txt.\n")
    f.write("- Developed Dockerfile.\n")
    f.write("- Wrote README.md documentation.\n")
    f.write("- Added changes to codebase log.\n")
