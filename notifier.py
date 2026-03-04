from discord_webhook import DiscordWebhook, DiscordEmbed
import config

class NotifierAgent:
    def __init__(self, webhook_url, bot_name="Job Intelligence Bot"):
        self.webhook_url = webhook_url
        self.bot_name = bot_name

    def send_notification(self, job):
        """Sends a notification with job details to the configured Discord Webhook."""
        if not self.webhook_url or self.webhook_url == "YOUR_DISCORD_WEBHOOK_HERE":
            print(f"[Notifier Agent] Discord Webhook URL not set. Cannot send notification for: {job.title}")
            return False

        print(f"[Notifier Agent] Sending Discord notification for {job.title}...")
        
        webhook = DiscordWebhook(url=self.webhook_url, username=self.bot_name)

        embed = DiscordEmbed(title=job.title, url=job.application_link, color="03b2f8")
        embed.set_author(name=job.company)
        
        embed.add_embed_field(name="Location", value=job.location, inline=True)
        embed.add_embed_field(name="Salary", value=job.salary, inline=True)
        
        desc_snippet = job.description[:250] + "..." if len(job.description) > 250 else job.description
        if desc_snippet:
             embed.add_embed_field(name="Description Snippet", value=desc_snippet, inline=False)
             
        embed.set_footer(text=f"Job ID: {job.job_id}")
        embed.set_timestamp()

        webhook.add_embed(embed)
        
        try:
            response = webhook.execute()
            if response.status_code == 200 or response.status_code == 204:
                print("[Notifier Agent] Notification sent successfully.")
                return True
            else:
                print(f"[Notifier Agent] Failed to send notification. Response: {response.status_code}")
                return False
        except Exception as e:
             print(f"[Notifier Agent] Exception sending webhook: {e}")
             return False
