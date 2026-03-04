import schedule
import time
import argparse
from datetime import datetime
import config
from scout import ScoutAgent
from filter import FilterAgent
from notifier import NotifierAgent
from database import db

def run_job_search(dry_run=False):
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting Job Search Cycle...")
    
    if not getattr(config, "JOB_PROFILES", None):
        print("[System] No JOB_PROFILES defined in config.py. Exiting cycle.")
        return

    scout = ScoutAgent()

    for profile in config.JOB_PROFILES:
        bot_name = profile.get("name", "Job Intelligence Bot")
        keywords = profile.get("keywords", [])
        webhook = profile.get("webhook_url", "")
        criteria = profile.get("criteria", {})
        
        print(f"\n[System] --- Running Profile: {bot_name} ---")
        if not keywords or not webhook:
            print(f"[System] Skipping {bot_name} due to missing keywords or webhook.")
            continue

        filter_agent = FilterAgent(criteria)
        notifier = NotifierAgent(webhook, bot_name)
        
        # 1. Scout for jobs
        all_found_jobs = scout.fetch_jobs(keywords)
        print(f"[System] {bot_name} Scout found {len(all_found_jobs)} total job cards.")
        
        # 2. Deduplicate
        new_jobs = []
        for job in all_found_jobs:
            if not db.is_job_processed(job.job_id):
                new_jobs.append(job)
            else:
                pass # Silent skip to avoid log spam
                
        print(f"[System] {bot_name} has {len(new_jobs)} unseen jobs remain after deduplication.")
        if not new_jobs:
            continue
            
        # 3. Filter
        matched_jobs = filter_agent.filter_jobs(new_jobs)
        print(f"[System] {bot_name} found {len(matched_jobs)} jobs that matched its criteria.")
        
        # 4. Notify & DB Write
        for job in matched_jobs:
            if not dry_run:
                success = notifier.send_notification(job)
                if success:
                    db.mark_job_processed(job.job_id)
            else:
                print(f"[Dry Run] {bot_name} would send notification for: {job.title} at {job.company}")
                pass
            
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Job Search Cycle Complete.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Real-time Job Intelligence Agent")
    parser.add_argument("--dry-run", action="store_true", help="Run once without sending notifications")
    parser.add_argument("--run-once", action="store_true", help="Run a single cycle without scheduling")
    args = parser.parse_args()
    
    if args.dry_run or args.run_once:
        print(f"[System] Executing single run (Dry Run: {args.dry_run})...")
        run_job_search(dry_run=args.dry_run)
        db.close()
    else:
        print(f"[System] Scheduling job search every {config.POLLING_INTERVAL_MINUTES} minutes...")
        # Run immediately on startup
        run_job_search()
        
        # Schedule future runs
        schedule.every(config.POLLING_INTERVAL_MINUTES).minutes.do(run_job_search)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("[System] Terminating job intelligence agent...")
        finally:
            db.close()
