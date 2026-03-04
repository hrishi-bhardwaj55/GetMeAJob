import os

# -------------------------------------------------------------------
# USER CONFIGURATION REQUIRED
# -------------------------------------------------------------------

# Common exclusion terms applied to all bots
_COMMON_EXCLUSIONS = [
    # Employment type
    "part time", "part-time", "contractor", "fixed duration", "fixed term", "temporary",
    # Entry level / student
    "intern", "internship", "co-op", "co op",
    # Citizenship / clearance
    "us citizen", "u.s. citizen", "must be a citizen", "clearance required",
    "security clearance", "active clearance", "secret clearance", "top secret",
    "ts/sci", "must be eligible to obtain",
]

# 1. Multi-Bot Job Profiles
# Define as many bots as you want. Each bot will map to a specific webhook and run its own search.
JOB_PROFILES = [
    {
        "name": "Software Engineering Bot",
        "tag": "sde",
        "keywords": ["Software Engineer", "Software Architect", "Senior Software Engineer", "Founding Engineer"],
        "location": "United States",
        "webhook_url": os.getenv("SWE_WEBHOOK_URL", "https://discord.com/api/webhooks/1478804759472509040/SJByynbKNhxp_8aBggdAS9jZ7eOARxdGXM8i0U8hEwFvyhG01H-UFAIUphjoooqQoKty"),
        "criteria": {
            "required_skills": [],
            "preferred_skills": [],
            "excluded_terms": _COMMON_EXCLUSIONS,
        }
    },
    {
        "name": "Data Science Bot",
        "tag": "data",
        "keywords": ["Data Scientist", "Data Engineer", "Data Analyst"],
        "location": "United States",
        "webhook_url": os.getenv("DATA_WEBHOOK_URL", "https://discord.com/api/webhooks/1478805330946162852/LApFy3EgwPKuuGf__dUH5nJpXLfbpXVIv9VfruISlNwbtmyDUgy13qAjxlYseddYn58G"),
        "criteria": {
            "required_skills": [],
            "preferred_skills": [],
            "excluded_terms": _COMMON_EXCLUSIONS,
        }
    },
    {
        "name": "AI/ML Bot",
        "tag": "ai",
        "keywords": ["AI Engineer", "AI Developer", "Machine Learning Engineer", "AI Roles"],
        "location": "United States",
        "webhook_url": os.getenv("AI_WEBHOOK_URL", "https://discord.com/api/webhooks/1478805030818812058/QJw9srckMwQ5AECXw7kbhLdTpsDhG-RGx5BwpS21OSiB8XgJuM-HoRexcJckW4kfKmha"),
        "criteria": {
            "required_skills": ["Python"],
            "preferred_skills": ["LLMs", "Agentic", "Prompt Engineering"],
            "excluded_terms": _COMMON_EXCLUSIONS,
            "threshold": 40.0
        }
    }
]

# General Settings
POLLING_INTERVAL_MINUTES = 60
DB_FILE = "jobs.db"
