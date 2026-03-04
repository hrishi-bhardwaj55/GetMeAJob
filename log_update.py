import os
import datetime

log_dir = r"c:\Projects\GetMeAJob\.agent\logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "chat_history.md")

with open(log_file, "a", encoding="utf-8") as f:
    f.write(f"\n\n## [{datetime.datetime.now().isoformat()}]\n")
    f.write("**Agent Reasoning**:\n")
    f.write("I replaced the Discord webhook snippet in config.py with SMTP credentials ")
    f.write("and updated the NotifierAgent in notifier.py to draft HTML emails via Python's smtplib. ")
    f.write("The system is now configured to send emails when live jobs are detected.\n\n")
    f.write("**Actions Taken**:\n")
    f.write("- Swapped webhook config for SMTP in config.py.\n")
    f.write("- Re-wrote notifier.py to use MIME and smtplib.\n")
