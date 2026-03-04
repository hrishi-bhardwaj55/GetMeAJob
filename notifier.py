from discord_webhook import DiscordWebhook, DiscordEmbed

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

        # ── Description snippet ───────────────────────────────────────────────
        desc = getattr(job, "description", "") or ""
        if desc and desc != "Description unavailable (LinkedIn blocked fetch)":
            snippet = desc[:300] + "…" if len(desc) > 300 else desc
            embed.add_embed_field(name="📄 Description", value=snippet, inline=False)
        elif desc == "Description unavailable (LinkedIn blocked fetch)":
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
