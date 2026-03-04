import os

# -------------------------------------------------------------------
# USER CONFIGURATION REQUIRED
# -------------------------------------------------------------------

# 1. Multi-Bot Job Profiles
# Define as many bots as you want. Each bot will map to a specific webhook and run its own search.
JOB_PROFILES = [
    {
        "name": "Software Engineering Bot",
        "keywords": ["Software Engineer", "Software Architect", "Senior Software Engineer", "Founding Engineer"],
        "location": "United States",
        "webhook_url": os.getenv("SWE_WEBHOOK_URL", "https://discord.com/api/webhooks/1478799507016781855/dR9SS_CRNuTKsczHzK69sN__mElJZaP1DvpKQZlP9_SKOvZln0bBl32DPlzzIHpAbf7U"),
        "criteria": {
            "required_skills": [],
            "preferred_skills": [],
            "excluded_terms": []
        }
    },
    {
        "name": "Data Science Bot",
        "keywords": ["Data Scientist", "Data Engineer", "Data Analyst"],
        "location": "United States",
        "webhook_url": os.getenv("DATA_WEBHOOK_URL", "https://discord.com/api/webhooks/1478799507016781855/dR9SS_CRNuTKsczHzK69sN__mElJZaP1DvpKQZlP9_SKOvZln0bBl32DPlzzIHpAbf7U"),
        "criteria": {
            "required_skills": [],
            "preferred_skills": [],
            "excluded_terms": []
        }
    },
    {
        "name": "AI/ML Bot",
        "keywords": ["AI Engineer", "AI Developer", "Machine Learning Engineer", "AI Roles"],
        "location": "United States",
        "webhook_url": os.getenv("AI_WEBHOOK_URL", "https://discord.com/api/webhooks/1478799507016781855/dR9SS_CRNuTKsczHzK69sN__mElJZaP1DvpKQZlP9_SKOvZln0bBl32DPlzzIHpAbf7U"),
        "criteria": {
            "required_skills": ["Python"],
            "preferred_skills": ["LLMs", "Agentic", "Prompt Engineering"],
            "excluded_terms": []
        }
    }
]

# General Settings
POLLING_INTERVAL_MINUTES = 60
DB_FILE = "jobs.db"
