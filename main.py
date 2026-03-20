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

    scout = ScoutAgent()
    
    if profile.get("use_ai", False):
        from ai_filter import AiFilterAgent
        filter_agent = AiFilterAgent(criteria, max_workers=5, api_key=getattr(config, "OPENAI_API_KEY", ""))

    else:
        filter_agent = FilterAgent(criteria, max_workers=5)
        
    notifier = NotifierAgent(webhook, bot_name)

    # 1. Scout
    all_found_jobs = scout.fetch_jobs(keywords, location=location)
    print(f"[System] {bot_name} → Scout found {len(all_found_jobs)} job cards.")

    # 2. Deduplicate against DB & within current batch
    unique_new_jobs = {}
    for job in all_found_jobs:
        if job.job_id not in unique_new_jobs and not db.is_job_processed(job.job_id):
            unique_new_jobs[job.job_id] = job
            
    new_jobs = list(unique_new_jobs.values())
    print(f"[System] {bot_name} → {len(new_jobs)} new unseen jobs after deduplication.")

    if not new_jobs:
        print(f"[System] {bot_name} → Nothing new. Skipping.")
        return

    # 3. Filter (concurrent internally)
    matched_jobs = filter_agent.filter_jobs(new_jobs)
    print(f"[System] {bot_name} → {len(matched_jobs)} jobs matched criteria.")

    # 4. Notify & DB Write
    sent, notify_failed = 0, 0
    matched_job_ids = {job.job_id for job in matched_jobs}
    
    # Mark rejected/skipped jobs as processed so we don't fetch and re-evaluate them on the next run
    if not dry_run:
        for job in new_jobs:
            if job.job_id not in matched_job_ids:
                db.mark_job_processed(job.job_id)

    for job in matched_jobs:
        if not dry_run:
            success = notifier.send_notification(job)
            if success:
                db.mark_job_processed(job.job_id)
                sent += 1
            else:
                notify_failed += 1
        else:
            summary = getattr(job, "job_summary", "Regex Passed")
            gap = getattr(job, "missing_from_resume", "None") 
            print(f"[Dry Run] {bot_name} → Would notify: {job.title} at {job.company} | AI Summary: {summary[:50]} | Gap: {gap[:50]}...")
            sent += 1

    # Jobs that were found but didn't match criteria
    skipped = len(new_jobs) - len(matched_jobs)

    if not dry_run:
        notifier.send_summary(sent=sent, rejected=notify_failed, skipped=skipped)

    print(f"[System] ✅ {bot_name} complete.")


def run_job_search(dry_run=False, bot_tags=None):
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚡ Starting Parallel Job Search Cycle...")

    if not getattr(config, "JOB_PROFILES", None):
        print("[System] No JOB_PROFILES defined in config.py. Exiting.")
        return

    # Filter profiles by tag if --bots was specified
    profiles = config.JOB_PROFILES
    if bot_tags:
        tags = {t.strip().lower() for t in bot_tags.split(",")}
        profiles = [p for p in profiles if p.get("tag", "").lower() in tags]
        if not profiles:
            print(f"[System] No profiles matched tags: {bot_tags}. Valid tags: {[p.get('tag') for p in config.JOB_PROFILES]}")
            return
        print(f"[System] Running selected bots: {[p['name'] for p in profiles]}")

    with ThreadPoolExecutor(max_workers=len(profiles)) as executor:
        futures = [executor.submit(run_profile, profile, dry_run) for profile in profiles]
        wait(futures)
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
    parser.add_argument("--bots", type=str, default=None,
                        help="Comma-separated bot tags to run (e.g. --bots sde,ai). Runs all if omitted.")
    args = parser.parse_args()

    if args.dry_run or args.run_once:
        print(f"[System] Executing single run (Dry Run: {args.dry_run})...")
        run_job_search(dry_run=args.dry_run, bot_tags=args.bots)
        db.close()
    else:
        print(f"[System] Scheduling job search every {config.POLLING_INTERVAL_MINUTES} minutes...")
        run_job_search(bot_tags=args.bots)

        schedule.every(config.POLLING_INTERVAL_MINUTES).minutes.do(
            run_job_search, bot_tags=args.bots
        )

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("[System] Terminating job intelligence agent...")
        finally:
            db.close()

