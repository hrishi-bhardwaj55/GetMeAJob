import schedule
import time
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, wait
import config
from scout import ScoutAgent
from filter import FilterAgent
from notifier import NotifierAgent
from database import db


def run_profile(profile, dry_run=False):
    """Runs the full scout → filter → notify pipeline for a single bot profile."""
    bot_name = profile.get("name", "Job Intelligence Bot")
    keywords = profile.get("keywords", [])
    webhook = profile.get("webhook_url", "")
    criteria = profile.get("criteria", {})
    location = profile.get("location", "United States")

    if not keywords or not webhook:
        print(f"[System] Skipping {bot_name} due to missing keywords or webhook.")
        return

    print(f"\n[System] ▶ Starting Profile: {bot_name}")

    # Each profile gets its own Scout, Filter, and Notifier instance
    scout = ScoutAgent()
    filter_agent = FilterAgent(criteria, max_workers=5)
    notifier = NotifierAgent(webhook, bot_name)

    # 1. Scout
    all_found_jobs = scout.fetch_jobs(keywords, location=location)
    print(f"[System] {bot_name} → Scout found {len(all_found_jobs)} job cards.")

    # 2. Deduplicate
    new_jobs = [job for job in all_found_jobs if not db.is_job_processed(job.job_id)]
    print(f"[System] {bot_name} → {len(new_jobs)} new unseen jobs after deduplication.")

    if not new_jobs:
        print(f"[System] {bot_name} → Nothing new. Skipping.")
        return

    # 3. Filter (concurrent internally)
    matched_jobs = filter_agent.filter_jobs(new_jobs)
    print(f"[System] {bot_name} → {len(matched_jobs)} jobs matched criteria.")

    # 4. Notify & DB Write
    for job in matched_jobs:
        if not dry_run:
            success = notifier.send_notification(job)
            if success:
                db.mark_job_processed(job.job_id)
        else:
            print(f"[Dry Run] {bot_name} → Would notify: {job.title} at {job.company}")

    print(f"[System] ✅ {bot_name} complete.")


def run_job_search(dry_run=False):
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚡ Starting Parallel Job Search Cycle...")

    if not getattr(config, "JOB_PROFILES", None):
        print("[System] No JOB_PROFILES defined in config.py. Exiting.")
        return

    # Run all bot profiles concurrently
    with ThreadPoolExecutor(max_workers=len(config.JOB_PROFILES)) as executor:
        futures = [
            executor.submit(run_profile, profile, dry_run)
            for profile in config.JOB_PROFILES
        ]
        wait(futures)

        # Surface any exceptions from threads
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"[System] Error in profile thread: {e}")

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ All Profiles Complete.\n")


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
        run_job_search()

        schedule.every(config.POLLING_INTERVAL_MINUTES).minutes.do(run_job_search)

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("[System] Terminating job intelligence agent...")
        finally:
            db.close()
