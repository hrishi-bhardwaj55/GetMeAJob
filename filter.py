import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import random

# Thread-local storage so each thread gets its own Playwright browser
_thread_local = threading.local()


def _get_thread_browser():
    """Returns a thread-local Playwright browser, creating it if needed."""
    if not hasattr(_thread_local, "playwright"):
        _thread_local.playwright = sync_playwright().start()
        _thread_local.browser = _thread_local.playwright.chromium.launch(headless=True)
    return _thread_local.browser


def _close_thread_browser():
    """Closes the thread-local browser if it exists."""
    if hasattr(_thread_local, "browser"):
        try:
            _thread_local.browser.close()
        except Exception:
            pass
    if hasattr(_thread_local, "playwright"):
        try:
            _thread_local.playwright.stop()
        except Exception:
            pass
    _thread_local.__dict__.clear()


def _fetch_description_in_thread(url):
    """Fetches a job description using the calling thread's own browser."""
    try:
        browser = _get_thread_browser()
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            time.sleep(random.uniform(0.5, 1.5))
            try:
                page.click("button.show-more-less-html__button", timeout=1500)
                time.sleep(0.3)
            except:
                pass
            content = page.content()
            soup = BeautifulSoup(content, "html.parser")
            desc_div = soup.find("div", class_="show-more-less-html__markup")
            return desc_div.get_text(" ", strip=True) if desc_div else ""
        finally:
            page.close()
    except Exception as e:
        return ""


class FilterAgent:
    def __init__(self, criteria_dict, max_workers=5):
        self.criteria = criteria_dict
        self.max_workers = max_workers

    def _evaluate_one(self, job):
        """Evaluates a single job. Runs in a worker thread with its own browser."""
        # Short-circuit: no criteria means everything passes
        if not self.criteria.get("required_skills") and \
           not self.criteria.get("preferred_skills") and \
           not self.criteria.get("excluded_terms"):
            job.description = "Filter bypassed (no criteria)"
            return job, 100.0

        description = _fetch_description_in_thread(job.application_link)
        job.description = description

        if not description:
            return job, 0.0

        desc_lower = description.lower()
        title_lower = job.title.lower()
        search_text = desc_lower + " " + title_lower

        # Check excluded terms
        for excluded in self.criteria.get("excluded_terms", []):
            if excluded.lower() in search_text:
                print(f"[Filter] ❌ Excluded '{excluded}': {job.title} @ {job.company}")
                return job, 0.0

        # Score required and preferred skills
        required = self.criteria.get("required_skills", [])
        preferred = self.criteria.get("preferred_skills", [])
        total_possible = len(required) * 2 + len(preferred)

        if total_possible == 0:
            return job, 100.0

        score = 0
        for skill in required:
            if re.search(rf"\b{re.escape(skill.lower())}\b", search_text):
                score += 2
        for skill in preferred:
            if re.search(rf"\b{re.escape(skill.lower())}\b", search_text):
                score += 1

        percentage = (score / total_possible) * 100
        return job, percentage

    def filter_jobs(self, jobs):
        """Evaluates jobs concurrently using a pool of worker threads, each with its own browser."""
        if not jobs:
            return []

        custom_threshold = float(self.criteria.get("threshold", 80.0))
        matched_jobs = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._evaluate_one, job): job for job in jobs}

            for future in as_completed(futures):
                try:
                    job, score = future.result()
                    if score >= custom_threshold:
                        print(f"[Filter] ✅ {job.title} @ {job.company} ({score:.0f}%)")
                        matched_jobs.append(job)
                    else:
                        print(f"[Filter] ❌ {job.title} @ {job.company} ({score:.0f}%)")
                except Exception as e:
                    print(f"[Filter] Error evaluating job: {e}")

        # Clean up thread-local browsers spawned during this pool run
        # (executor threads are reused, so we trigger cleanup manually after pool closes)
        return matched_jobs
