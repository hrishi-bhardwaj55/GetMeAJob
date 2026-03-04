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
# Discord Webhook Settings (For Server Channels)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/1478799507016781855/dR9SS_CRNuTKsczHzK69sN__mElJZaP1DvpKQZlP9_SKOvZln0bBl32DPlzzIHpAbf7U")

# General Settings
POLLING_INTERVAL_MINUTES = 60
DB_FILE = "jobs.db"
