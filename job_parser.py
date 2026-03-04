import re

# ──────────────────────────────────────────────
# Salary extraction
# ──────────────────────────────────────────────

_SALARY_PATTERNS = [
    # $120,000 - $180,000 / $120K - $180K
    r'\$[\d,]+[kK]?\s*[-–to]+\s*\$[\d,]+[kK]?(?:\s*/\s*(?:yr|year|annual|hr|hour|hour))?',
    # $120,000 or $120K standalone
    r'\$[\d,]+[kK](?:\s*/\s*(?:yr|year|hr|hour))?',
    # 120,000 - 180,000 (USD) style
    r'[\d,]+\s*[-–]\s*[\d,]+\s*(?:USD|CAD|GBP)?(?:\s*/\s*(?:yr|year|annual|hr|hour))?',
    # Up to $200K
    r'up to \$[\d,]+[kK]?',
]

_SALARY_RE = re.compile('|'.join(_SALARY_PATTERNS), re.IGNORECASE)


def extract_salary(text):
    """Returns the first salary-like pattern found in text, or None."""
    match = _SALARY_RE.search(text)
    return match.group(0).strip() if match else None


# ──────────────────────────────────────────────
# Experience extraction
# ──────────────────────────────────────────────

_EXP_RE = re.compile(
    r'(\d+\+?\s*(?:–|-|to)\s*\d+|\d+\+?)\s*'
    r'(?:years?|yrs?)(?:\s+of)?\s*(?:of\s+)?(?:professional\s+)?experience',
    re.IGNORECASE
)


def extract_experience(text):
    """Returns the experience requirement string found in text, or None."""
    match = _EXP_RE.search(text)
    return match.group(0).strip() if match else None


# ──────────────────────────────────────────────
# Tech skills extraction
# ──────────────────────────────────────────────

KNOWN_SKILLS = [
    # Languages
    "Python", "Java", "JavaScript", "TypeScript", "Go", "Golang", "Rust", "C++", "C#", "Ruby",
    "Swift", "Kotlin", "Scala", "R", "MATLAB", "Bash", "Shell",
    # Web / Frontend
    "React", "Angular", "Vue", "Next.js", "Node.js", "HTML", "CSS", "GraphQL", "REST", "gRPC",
    # Data / ML / AI
    "TensorFlow", "PyTorch", "Keras", "scikit-learn", "Pandas", "NumPy", "Spark", "Kafka",
    "Airflow", "dbt", "Hadoop", "Hive", "LLM", "LLMs", "Transformers", "HuggingFace",
    "OpenAI", "LangChain", "RAG", "Prompt Engineering", "MLflow", "Vertex AI", "SageMaker",
    # Cloud / Infra
    "AWS", "GCP", "Azure", "Kubernetes", "Docker", "Terraform", "Ansible", "CI/CD",
    "GitHub Actions", "Jenkins", "Linux",
    # Databases
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Cassandra", "Snowflake", "BigQuery",
    "DynamoDB", "Elasticsearch",
    # Other
    "Microservices", "API", "Git", "Agile", "Scrum",
]

_SKILL_PATTERN = re.compile(
    r'\b(' + '|'.join(re.escape(s) for s in KNOWN_SKILLS) + r')\b',
    re.IGNORECASE
)


def extract_skills(text):
    """Returns a deduplicated, sorted list of recognised tech skills found in text."""
    found = {m.group(0) for m in _SKILL_PATTERN.finditer(text)}
    # Normalise case using the canonical name from KNOWN_SKILLS
    canonical = {s.lower(): s for s in KNOWN_SKILLS}
    return sorted({canonical.get(s.lower(), s) for s in found})
