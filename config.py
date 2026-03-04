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
# Email SMTP Settings (Defaulting to Gmail)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "YOUR_EMAIL@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "YOUR_APP_PASSWORD") # Use an App Password if using Gmail
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "YOUR_RECEIVER_EMAIL@domain.com")

# General Settings
POLLING_INTERVAL_MINUTES = 60
DB_FILE = "jobs.db"
