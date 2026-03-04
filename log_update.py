import os
import datetime

log_dir = r"c:\Projects\GetMeAJob\.agent\logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "chat_history.md")

with open(log_file, "a", encoding="utf-8") as f:
    f.write(f"\n\n## [{datetime.datetime.now().isoformat()}]\n")
    f.write("**Agent Reasoning**:\n")
    f.write("I installed discord.py, updated config.py with bot token fields, ")
    f.write("and completely rewrote notifier.py out of SMTP into an asynchronous discord Bot script ")
    f.write("that logs in, fetches the targeted user by their ID, drops a rich embed DM, and cleanly logs out.\n\n")
    f.write("**Actions Taken**:\n")
    f.write("- Swapped SMTP config for DISCORD_BOT_TOKEN and DISCORD_USER_ID.\n")
    f.write("- Implemented async Discord.py logic in notifier.py.\n")
