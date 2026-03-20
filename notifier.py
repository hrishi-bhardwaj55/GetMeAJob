from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime, timezone


def _format_posted_time(posted_at):
    """Returns (absolute_str, relative_str) for a job's posted_at datetime."""
    if not posted_at:
        return None, None
    
    now = datetime.now(tz=timezone.utc)
    # Ensure posted_at is timezone-aware
    if posted_at.tzinfo is None:
        posted_at = posted_at.replace(tzinfo=timezone.utc)
    
    delta = now - posted_at
    total_seconds = int(delta.total_seconds())
    
    if total_seconds < 60:
        relative = f"{total_seconds}s ago"
    elif total_seconds < 3600:
        mins = total_seconds // 60
        relative = f"{mins} min ago" if mins == 1 else f"{mins} mins ago"
    elif total_seconds < 86400:
        hours = total_seconds // 3600
        relative = f"{hours} hr ago" if hours == 1 else f"{hours} hrs ago"
    else:
        days = total_seconds // 86400
        relative = f"{days} day ago" if days == 1 else f"{days} days ago"
    
    absolute = posted_at.strftime("%b %d, %Y %I:%M %p UTC")
    return absolute, relative


class NotifierAgent:
    def __init__(self, webhook_url, bot_name="Job Intelligence Bot"):
        self.webhook_url = webhook_url
        self.bot_name = bot_name

    def send_notification(self, job):
        """Sends a rich Discord embed notification with all parsed job details."""
        if not self.webhook_url or self.webhook_url == "YOUR_DISCORD_WEBHOOK_HERE":
            print(f"[Notifier Agent] Webhook not set. Skipping: {job.title}")
            return False

        print(f"[Notifier Agent] Sending Discord notification for {job.title}...")

        webhook = DiscordWebhook(
            url=self.webhook_url,
            username=self.bot_name,
            rate_limit_retry=True
        )

        embed = DiscordEmbed(title=job.title, url=job.application_link, color="03b2f8")
        embed.set_author(name=job.company)

        # ── Core fields (always present) ──────────────────────────────────────
        embed.add_embed_field(name="📍 Location", value=job.location or "Not specified", inline=True)

        # Salary: prefer parsed description salary over card-level salary
        salary_display = (
            getattr(job, "parsed_salary", None)
            or (job.salary if job.salary != "Not Listed" else None)
            or "Not Listed"
        )
        embed.add_embed_field(name="💰 Salary", value=salary_display, inline=True)

        # Posted time — use LinkedIn's own relative text (e.g. "32 minutes ago")
        posted_time = getattr(job, "posted_time_text", None)
        if posted_time:
            embed.add_embed_field(name="🕐 Posted", value=posted_time, inline=True)

        # ── Parsed fields (from full description) ─────────────────────────────
        experience = getattr(job, "parsed_experience", None)
        if experience:
            embed.add_embed_field(name="🗓 Experience", value=experience.capitalize(), inline=True)

        skills = getattr(job, "parsed_skills", [])
        if skills:
            # Show up to 15 skills as comma-separated tags, capped at 1024 chars
            skills_text = ", ".join(f"`{s}`" for s in skills[:15])
            if len(skills) > 15:
                skills_text += f" +{len(skills) - 15} more"
            embed.add_embed_field(name="🛠 Skills Detected", value=skills_text, inline=False)

        # ── AI Summary & Description ──────────────────────────────────────────
        ai_summary = getattr(job, "job_summary", "")
        if ai_summary and "Error" not in ai_summary and "Could not fetch" not in ai_summary:
            embed.add_embed_field(name="✨ AI Summary", value=ai_summary, inline=False)
            
        ai_gap = getattr(job, "missing_from_resume", "")
        if ai_gap and ai_gap.lower() not in ["none", "n/a", "none.", "n/a."]:
            embed.add_embed_field(name="🎯 Resume Gap", value=f"_{ai_gap}_", inline=False)

        desc = getattr(job, "description", "") or ""
        desc_blocked = (desc == "Description unavailable (LinkedIn blocked fetch)" or "Could not fetch" in ai_summary)

        if desc and not desc_blocked and not ai_summary:
            snippet = desc[:300] + "…" if len(desc) > 300 else desc
            embed.add_embed_field(name="📄 Description", value=snippet, inline=False)
        elif desc_blocked:
            embed.add_embed_field(name="📄 Description", value="⚠️ LinkedIn blocked the description fetch — click to view.", inline=False)

        embed.set_footer(text=f"Job ID: {job.job_id}")
        embed.set_timestamp()
        webhook.add_embed(embed)

        try:
            response = webhook.execute()
            if response.status_code in (200, 204):
                print("[Notifier Agent] Notification sent successfully.")
                return True
            else:
                print(f"[Notifier Agent] Failed. Response: {response.status_code}")
                return False
        except Exception as e:
            print(f"[Notifier Agent] Exception: {e}")
            return False

    def send_summary(self, sent: int, rejected: int, skipped: int):
        """Sends a compact completion message to Discord after a bot's cycle finishes."""
        if not self.webhook_url or self.webhook_url == "YOUR_DISCORD_WEBHOOK_HERE":
            return

        from datetime import datetime, timezone
        now = datetime.now(tz=timezone.utc).strftime("%b %d, %Y %I:%M %p UTC")

        if sent == 0:
            color = "808080"  # grey — nothing new
            title = "✅ Scan Complete — No New Jobs"
        else:
            color = "2ecc71"  # green — jobs were sent
            title = f"✅ Scan Complete — {sent} Job{'s' if sent != 1 else ''} Sent"

        embed = DiscordEmbed(title=title, color=color)
        embed.add_embed_field(name="📤 Sent",     value=str(sent),     inline=True)
        embed.add_embed_field(name="❌ Rejected", value=str(rejected), inline=True)
        embed.add_embed_field(name="⏭ Skipped",  value=str(skipped),  inline=True)
        embed.set_footer(text=f"Completed at {now}")
        embed.set_timestamp()

        webhook = DiscordWebhook(url=self.webhook_url, username=self.bot_name, rate_limit_retry=True)
        webhook.add_embed(embed)
        try:
            webhook.execute()
        except Exception as e:
            print(f"[Notifier Agent] Failed to send summary: {e}")
