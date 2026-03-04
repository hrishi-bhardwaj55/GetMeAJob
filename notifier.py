import discord
import asyncio
import config
from discord.ext import commands

class NotifierAgent:
    def __init__(self):
        self.token = config.DISCORD_BOT_TOKEN
        self.user_id = config.DISCORD_USER_ID

    async def _send_async_notification(self, job):
        """Asynchronous helper to send the DM"""
        intents = discord.Intents.default()
        bot = commands.Bot(command_prefix="!", intents=intents)

        @bot.event
        async def on_ready():
            try:
                # Fetch the user to DM based on their ID
                user = await bot.fetch_user(self.user_id)
                if user:
                    embed = discord.Embed(title=job.title, url=job.application_link, color=0x03b2f8)
                    embed.set_author(name=job.company)
                    embed.add_field(name="Location", value=job.location, inline=True)
                    embed.add_field(name="Salary", value=job.salary, inline=True)
                    
                    desc_snippet = job.description[:250] + "..." if len(job.description) > 250 else job.description
                    if desc_snippet:
                        embed.add_field(name="Description Snippet", value=desc_snippet, inline=False)
                        
                    embed.set_footer(text=f"Job ID: {job.job_id}")
                    
                    await user.send(embed=embed)
                    print(f"[Notifier Agent] Sent DM to {user.name} for {job.title}")
                else:
                    print(f"[Notifier Agent] Could not find user with ID {self.user_id}")
            except Exception as e:
                print(f"[Notifier Agent] Error sending DM: {e}")
            finally:
                # Close the bot connection after sending
                await bot.close()
                
        # Start the bot
        await bot.start(self.token)

    def send_notification(self, job):
        """Synchronous wrapper to be called by main.py"""
        if self.token == "YOUR_BOT_TOKEN_HERE" or self.user_id == "YOUR_DISCORD_USER_ID_HERE":
            print(f"[Notifier Agent] Discord Bot not configured. Cannot send DM for: {job.title}")
            return False
            
        print(f"[Notifier Agent] Preparing Discord DM for {job.title}...")
        
        try:
            # We must run the bot in a separate event loop since main.py is synchronous
            asyncio.run(self._send_async_notification(job))
            return True
        except Exception as e:
            print(f"[Notifier Agent] Failed during async execution: {e}")
            return False
