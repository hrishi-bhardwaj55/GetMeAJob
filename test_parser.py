import job_parser as p

salary_text = "Base pay: $130,000 - $180,000 per year. Also eligible for bonus."
exp_text = "We require 5+ years of professional experience in software development."
skills_text = "Must know Python, AWS, Docker, React, Kubernetes, and PostgreSQL."

s = p.extract_salary(salary_text)
e = p.extract_experience(exp_text)
sk = p.extract_skills(skills_text)

print(f"Salary:     {s!r}")
print(f"Experience: {e!r}")
print(f"Skills:     {sk}")

assert s == "$130,000 - $180,000", f"Expected salary, got: {s!r}"
assert e is not None and "5+" in e
assert "Python" in sk and "AWS" in sk
print("\n✅ All parser tests passed!")
