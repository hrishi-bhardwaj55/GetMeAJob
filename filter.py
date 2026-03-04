import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import random

class FilterAgent:
    def __init__(self, criteria_dict, max_workers=5):
        self.criteria = criteria_dict
        self.max_workers = max_workers
        self._playwright = None
        self._browser = None
        self._browser_lock = threading.Lock()

    def _start_browser(self):
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=True)

    def _stop_browser(self):
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
        self._browser = None
        self._playwright = None

    def _fetch_description(self, url):
        """Fetches the full job description text (each call opens a new page in the shared browser)."""
        try:
            with self._browser_lock:
                page = self._browser.new_page(
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

    def _evaluate_one(self, job):
        """Evaluates a single job's description against criteria. Returns (job, score)."""

        # Short-circuit: no criteria means everything passes
        if not self.criteria.get("required_skills") and not self.criteria.get("preferred_skills") and not self.criteria.get("excluded_terms"):
            job.description = "Filter bypassed (no criteria)"
            return job, 100.0

        description = self._fetch_description(job.application_link)
        job.description = description

        if not description:
            return job, 0.0

        desc_lower = description.lower()
        title_lower = job.title.lower()
        search_text = desc_lower + " " + title_lower

        # Check excluded terms immediately
        for excluded in self.criteria.get("excluded_terms", []):
            if excluded.lower() in search_text:
                print(f"[Filter Agent] ❌ Excluded '{excluded}': {job.title} at {job.company}")
                return job, 0.0

        # Calculate score
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
        """Evaluates jobs concurrently and returns ones >= threshold."""
        if not jobs:
            return []

        custom_threshold = float(self.criteria.get("threshold", 80.0))

        needs_fetch = (
            self.criteria.get("required_skills") or
            self.criteria.get("preferred_skills") or
            self.criteria.get("excluded_terms")
        )

        if needs_fetch:
            self._start_browser()

        matched_jobs = []
        try:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(self._evaluate_one, job): job for job in jobs}

                for future in as_completed(futures):
                    try:
                        job, score = future.result()
                        if score >= custom_threshold:
                            print(f"[Filter Agent] ✅ Match! {job.title} at {job.company} ({score:.0f}%)")
                            matched_jobs.append(job)
                        else:
                            print(f"[Filter Agent] ❌ Rejected {job.title} at {job.company} ({score:.0f}%)")
                    except Exception as e:
                        print(f"[Filter Agent] Error evaluating job: {e}")
        finally:
            if needs_fetch:
                self._stop_browser()

        return matched_jobs
