import time
import random
import urllib.parse
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import config

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.2365.92"
]

class Job:
    def __init__(self, job_id, title, company, location, application_link, salary="Not Listed", description="", posted_time_text=None):
        self.job_id = job_id
        self.title = title
        self.company = company
        self.location = location
        self.application_link = application_link
        self.salary = salary
        self.description = description
        self.posted_time_text = posted_time_text  # e.g. "32 minutes ago" (from LinkedIn)
        # Parsed from full description by FilterAgent
        self.parsed_salary = None
        self.parsed_experience = None
        self.parsed_skills = []

class ScoutAgent:
    def __init__(self):
        self.base_url = "https://www.linkedin.com/jobs/search?"

    def _get_random_user_agent(self):
        return random.choice(USER_AGENTS)

    def _human_delay(self, min_sec=2, max_sec=5):
        time.sleep(random.uniform(min_sec, max_sec))

    def fetch_jobs(self, keywords, location="United States"):
        """Scrapes LinkedIn for job listings matching keywords (Past 24 Hours, Most Recent)."""
        jobs_found = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=self._get_random_user_agent(),
                viewport={'width': random.randint(1024, 1920), 'height': random.randint(768, 1080)}
            )
            page = context.new_page()

            # Combine keywords into a single Boolean OR query to speed up search
            # Example: ("Software Engineer" OR "SDE 1" OR "Software Architect")
            bundled_query = " OR ".join([f'"{kw}"' for kw in keywords])
            
            # f_TPR=r86400 -> Past 24 hours
            # sortBy=DD -> Most recent
            params = {
                "keywords": bundled_query,
                "location": location,
                "f_TPR": "r3600",  # 3600 seconds = 1 hour
                "f_JT": "F",       # Full-time jobs only
                "sortBy": "DD"
            }
            
            # Append exact geoId for United States to prevent international contamination
            if "united states" in location.lower() or location.lower() == "us":
                params["geoId"] = "103644278"
            
            query_string = urllib.parse.urlencode(params)
            search_url = f"{self.base_url}{query_string}"
            
            print(f"[Scout Agent] Searching for bundled query: {bundled_query}")
            
            try:
                page.goto(search_url, wait_until="domcontentloaded")
                self._human_delay(3, 7)
                
                # Scroll down to load more jobs (simulate human behavior)
                # Keep scrolling until no new jobs are loaded, exhausting the "Past Hour" feed
                previous_job_count = 0
                stagnant_scrolls = 0
                max_scrolls = 50 # Hard cap just to prevent true infinite loops
                
                for current_scroll in range(max_scrolls):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                    self._human_delay(1, 2)
                    
                    # Try to click the "See more jobs" button if it appears
                    try:
                        # LinkedIn uses various classes for this button over time
                        see_more_btn = page.query_selector("button.infinite-scroller__show-more-button")
                        if see_more_btn and see_more_btn.is_visible():
                            see_more_btn.click()
                            self._human_delay(1, 2)
                    except Exception:
                        pass
                    
                    # Verify if scrolling actually loaded new items in the DOM
                    current_job_count = page.locator("div.base-card").count()
                    if current_job_count <= previous_job_count:
                        stagnant_scrolls += 1
                        # If we scroll 3 times and no new jobs appear, we've hit the bottom or an auth-wall
                        if stagnant_scrolls >= 3:
                            print(f"[Scout Agent] Reached bottom of feed or auth-wall after {current_scroll} scrolls.")
                            break
                    else:
                        stagnant_scrolls = 0  # Reset
                        previous_job_count = current_job_count
                    
                content = page.content()
                soup = BeautifulSoup(content, "html.parser")
                
                job_cards = soup.find_all("div", class_="base-card")
                
                print(f"[Scout Agent] Found {len(job_cards)} job cards for bundled query. Extracting details...")
                
                for card in job_cards:
                    job_id = card.get("data-entity-urn", "").split(":")[-1]
                    if not job_id:
                        continue
                        
                    title_el = card.find("h3", class_="base-search-card__title")
                    company_el = card.find("h4", class_="base-search-card__subtitle")
                    location_el = card.find("span", class_="job-search-card__location")
                    salary_el = card.find("span", class_="job-search-card__salary-info")
                    link_el = card.find("a", class_="base-card__full-link")
                    time_el = card.find("time")
                    
                    title = title_el.text.strip() if title_el else "Unknown Title"
                    company = company_el.text.strip() if company_el else "Unknown Company"
                    location = location_el.text.strip() if location_el else "Unknown Location"
                    salary = salary_el.text.strip() if salary_el else "Not Listed"
                    link = link_el["href"].split("?")[0] if link_el and "href" in link_el.attrs else ""
                    
                    # Use LinkedIn's own relative time text (e.g. "32 minutes ago")
                    # The datetime attribute only has the date, not the time, so we avoid it.
                    posted_time_text = time_el.get_text(strip=True) if time_el else None
                    
                    jobs_found.append(Job(job_id, title, company, location, link, salary, description="", posted_time_text=posted_time_text))
                    
            except Exception as e:
                print(f"[Scout Agent] Error fetching jobs for bundled query: {e}")
                
            browser.close()
            
        return jobs_found
