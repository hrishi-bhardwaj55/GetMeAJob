import os

# -------------------------------------------------------------------
# USER CONFIGURATION REQUIRED
# -------------------------------------------------------------------

# 1. Keywords for the Scout Agent to search on LinkedIn
SEARCH_KEYWORDS = [
    "Software Engineer",
    "Systems Architect",
    # Add more keywords here
]

# 2. Roles/Criteria for the Filter Agent to match against
# The Filter Agent will parse job descriptions to calculate a match score.
# Example: 
# MATCH_CRITERIA = {
#     "required_skills": ["Python", "Playwright", "System Architecture"],
#     "preferred_skills": ["Docker", "AWS"],
#     "excluded_terms": ["Unpaid", "Internship"]
# }
MATCH_CRITERIA = {
    "required_skills": [],
    "preferred_skills": [],
    "excluded_terms": []
}

# 3. Notification Platform Configuration
# Discord Bot Settings (For Direct Messages)
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID", "YOUR_DISCORD_USER_ID_HERE")

# General Settings
POLLING_INTERVAL_MINUTES = 60
DB_FILE = "jobs.db"
