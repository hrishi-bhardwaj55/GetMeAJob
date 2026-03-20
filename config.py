import os

# -------------------------------------------------------------------

# AI Configuration
# -------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")



# -------------------------------------------------------------------
# USER CONFIGURATION REQUIRED
# -------------------------------------------------------------------

USER_RESUME = """
Hrishikesh Bhardwaj
Master of Software Engineering | Carnegie Mellon University
~5 Years Professional Software Engineering Experience

SKILLS: Python, Java, Golang, C++, Scala, Kafka, Spark, AWS, Azure, GCP, Kubernetes, Docker.

PROFESSIONAL EXPERIENCE:
ION Group | Software Developer 2 (Aug 2023 - Jul 2025)
- Led team delivering 30+ features for CDS trading.
- Led Java upgrade from 8 to 21 for 10M+ LOC FX platform.
- Engineered in-memory caching system.

ION Group | Software Developer (Feb 2021 - Aug 2023)
- Developed flagship software XTP using Java and Agile.
- Boosted market data processing time by 90%.

CDAC | Software Development Intern (May 2019 - Jun 2019)

PROJECTS:
- Twitter User Recommendation System (ETL, Kubernetes, Java, Spring Boot)
- Stream Processing with Kafka and Samza
- Quorum-Based Replication with Raft (Golang)
"""

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
        "keywords": ["Software Engineer", "Software Architect", "Senior Software Engineer", "Founding Engineer", "SDE 1", "SDE 2", "Software Development Engineer"],
        "location": "United States",
        "webhook_url": os.getenv("SWE_WEBHOOK_URL", "https://discord.com/api/webhooks/1478804759472509040/SJByynbKNhxp_8aBggdAS9jZ7eOARxdGXM8i0U8hEwFvyhG01H-UFAIUphjoooqQoKty"),
        "criteria": {
            "required_skills": [],
            "preferred_skills": [],
            "excluded_terms": _COMMON_EXCLUSIONS,
        },
        "use_ai": True

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
        },
        "use_ai": True

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
        },
        "use_ai": True

    }
]

# General Settings
POLLING_INTERVAL_MINUTES = 60
DB_FILE = "jobs.db"
