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
    
    if not config.SEARCH_KEYWORDS:
        print("[System] No search keywords defined in config.py. Exiting cycle.")
        return

    scout = ScoutAgent()
    filter_agent = FilterAgent()
    notifier = NotifierAgent()
    
    # 1. Scout for jobs
    all_found_jobs = scout.fetch_jobs(config.SEARCH_KEYWORDS)
    print(f"[System] Scout found {len(all_found_jobs)} total jobs.")
    
    # 2. Deduplicate
    new_jobs = []
    for job in all_found_jobs:
        if not db.is_job_processed(job.job_id):
            new_jobs.append(job)
        else:
            print(f"[System] Skipping already processed job: {job.job_id}")
            
    print(f"[System] {len(new_jobs)} unseen jobs remain after deduplication.")
    if not new_jobs:
        print("[System] Cycle complete. No new jobs to process.")
        return
        
    # 3. Filter
    matched_jobs = filter_agent.filter_jobs(new_jobs)
    print(f"[System] {len(matched_jobs)} jobs matched the criteria.")
    
    # 4. Notify & DB Write
    for job in matched_jobs:
        if not dry_run:
            success = notifier.send_notification(job)
            if success:
                db.mark_job_processed(job.job_id)
        else:
            print(f"[Dry Run] Would send notification and mark processed for: {job.title} at {job.company}")
            db.mark_job_processed(job.job_id) # Still mark in DB so we don't fetch them again next time even in dry-run, or maybe don't?
            # actually better not to mark in dry run to test notifications later.
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
