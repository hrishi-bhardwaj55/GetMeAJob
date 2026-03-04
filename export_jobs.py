from scout import ScoutAgent
from filter import FilterAgent
import config

def export_jobs_to_file():
    scout = ScoutAgent()
    filter_agent = FilterAgent()
    
    print("Fetching jobs...")
    jobs = scout.fetch_jobs(config.SEARCH_KEYWORDS)
    
    print(f"Scout found {len(jobs)} total jobs. Filtering...")
    matched_jobs = filter_agent.filter_jobs(jobs)
    
    print(f"Filter matched {len(matched_jobs)} jobs. Writing to jobs_output.txt...")
    with open("jobs_output.txt", "w", encoding="utf-8") as f:
        f.write(f"Found {len(matched_jobs)} matching jobs based on your criteria:\n\n")
        for job in matched_jobs:
            f.write(f"Job Title: {job.title}\n")
            f.write(f"Company: {job.company}\n")
            f.write(f"Location: {job.location}\n")
            f.write(f"Salary: {job.salary}\n")
            f.write(f"Application Link: {job.application_link}\n")
            f.write("-" * 50 + "\n")
            
    print("Done.")

if __name__ == "__main__":
    export_jobs_to_file()
