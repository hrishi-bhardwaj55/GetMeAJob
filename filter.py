import re
import config
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import random

class FilterAgent:
    def __init__(self, criteria_dict):
        self.criteria = criteria_dict

    def _fetch_description(self, url):
        """Fetches the full job description text from a job page URL"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            try:
                page.goto(url, wait_until="domcontentloaded")
                time.sleep(random.uniform(2, 4))
                
                # Check for "show more" button
                try:
                    page.click("button.show-more-less-html__button", timeout=2000)
                    time.sleep(1)
                except:
                    pass
                
                content = page.content()
                soup = BeautifulSoup(content, "html.parser")
                desc_div = soup.find("div", class_="show-more-less-html__markup")
                desc_text = desc_div.get_text(" ", strip=True) if desc_div else soup.get_text(" ", strip=True)
                
                browser.close()
                return desc_text
            except Exception as e:
                browser.close()
                print(f"[Filter Agent] Error fetching description: {e}")
                return ""

    def evaluate_job(self, job):
        """
        Evaluates the job description against the criteria and returns a score (0 to 100).
        """
        print(f"[Filter Agent] Evaluating job: {job.title} at {job.company}")
        
        # 1. Fetch description
        # Limit fetches only if absolutely necessary, but since we need description matching...
        # If there are no skills configured, we can skip fetching description entirely and pass.
        if not self.criteria.get("required_skills") and not self.criteria.get("preferred_skills") and not self.criteria.get("excluded_terms"):
            print("[Filter Agent] No criteria provided. Bypassing filter with 100% score.")
            job.description = "Filter bypassed (no criteria)"
            return 100.0

        description = self._fetch_description(job.application_link)
        job.description = description
        
        if not description:
            print(f"[Filter Agent] Unable to get description for {job.job_id}. Rejecting.")
            return 0.0
            
        desc_lower = description.lower()
        title_lower = job.title.lower()
        search_text = desc_lower + " " + title_lower
        
        # 2. Check excluded terms immediately
        for excluded in self.criteria.get("excluded_terms", []):
            if excluded.lower() in search_text:
                print(f"[Filter Agent] Job contains excluded term '{excluded}'. Rejecting.")
                return 0.0
                
        # 3. Calculate score based on required and preferred skills
        required = self.criteria.get("required_skills", [])
        preferred = self.criteria.get("preferred_skills", [])
        
        total_possible = len(required) * 2 + len(preferred)
        
        if total_possible == 0:
            return 100.0 # No positive criteria, but didn't trigger excluded.
            
        score = 0
        for skill in required:
            # Simple boundary match
            if re.search(rf"\b{re.escape(skill.lower())}\b", search_text):
                 score += 2
                 
        for skill in preferred:
            if re.search(rf"\b{re.escape(skill.lower())}\b", search_text):
                 score += 1
                 
        percentage = (score / total_possible) * 100
        print(f"[Filter Agent] Match score for {job.job_id}: {percentage:.1f}%")
        
        return percentage

    def filter_jobs(self, jobs):
        """Receives a list of jobs, evaluates them, and returns ones >= threshold"""
        matched_jobs = []
        
        # Look for a custom threshold in the criteria, otherwise default to 80.0
        custom_threshold = float(self.criteria.get("threshold", 80.0))
        
        for job in jobs:
            score = self.evaluate_job(job)
            if score >= custom_threshold:
                print(f"[Filter Agent] Match! {job.title} at {job.company} scored {score:.1f}% (Threshold: {custom_threshold}%)")
                matched_jobs.append(job)
            else:
                print(f"[Filter Agent] Rejected {job.title} at {job.company} (Score: {score:.1f}% < {custom_threshold}%)")
        return matched_jobs
