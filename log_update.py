import os
import datetime

log_dir = r"c:\Projects\GetMeAJob\.agent\logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "chat_history.md")

with open(log_file, "a", encoding="utf-8") as f:
    f.write(f"\n\n## [{datetime.datetime.now().isoformat()}]\n")
    f.write("**Agent Reasoning**:\n")
    f.write("I re-installed the discord-webhook library and completely discarded the complex discord.py bot logic. ")
    f.write("The configuration file now requires a simple DISCORD_WEBHOOK_URL again, and the NotifierAgent directly pushes the embed payload synchronously.\n\n")
    f.write("**Actions Taken**:\n")
    f.write("- Reverted `config.py` variables to `DISCORD_WEBHOOK_URL`.\n")
    f.write("- Reverted `notifier.py` back to using the `DiscordWebhook` payload.\n")
    f.write("- Finalized the task list and notified the user to setup their server channel webhook.\n")
