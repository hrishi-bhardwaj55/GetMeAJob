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
    def __init__(self, job_id, title, company, location, application_link, salary="Not Listed", description=""):
        self.job_id = job_id
        self.title = title
        self.company = company
        self.location = location
        self.application_link = application_link
        self.salary = salary
        self.description = description

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

            for keyword in keywords:
                # f_TPR=r86400 -> Past 24 hours
                # sortBy=DD -> Most recent
                params = {
                    "keywords": keyword,
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
                
                print(f"[Scout Agent] Searching for: '{keyword}'...")
                
                try:
                    page.goto(search_url, wait_until="domcontentloaded")
                    self._human_delay(3, 7)
                    
                    # Scroll down to load more jobs (simulate human behavior)
                    for _ in range(3):
                        page.evaluate("window.scrollBy(0, document.body.scrollHeight/3);")
                        self._human_delay(1, 3)
                        
                    content = page.content()
                    soup = BeautifulSoup(content, "html.parser")
                    
                    job_cards = soup.find_all("div", class_="base-card")
                    
                    print(f"[Scout Agent] Found {len(job_cards)} job cards for '{keyword}'. Extracting details...")
                    
                    for card in job_cards:
                        job_id = card.get("data-entity-urn", "").split(":")[-1]
                        if not job_id:
                            continue
                            
                        title_el = card.find("h3", class_="base-search-card__title")
                        company_el = card.find("h4", class_="base-search-card__subtitle")
                        location_el = card.find("span", class_="job-search-card__location")
                        salary_el = card.find("span", class_="job-search-card__salary-info")
                        link_el = card.find("a", class_="base-card__full-link")
                        
                        title = title_el.text.strip() if title_el else "Unknown Title"
                        company = company_el.text.strip() if company_el else "Unknown Company"
                        location = location_el.text.strip() if location_el else "Unknown Location"
                        salary = salary_el.text.strip() if salary_el else "Not Listed"
                        link = link_el["href"].split("?")[0] if link_el and "href" in link_el.attrs else ""
                        
                        # We won't fetch full description yet to save time and reduce detection risk. 
                        # We just instantiate the job object with early data.
                        jobs_found.append(Job(job_id, title, company, location, link, salary, description=""))
                        
                except Exception as e:
                    print(f"[Scout Agent] Error fetching jobs for {keyword}: {e}")
                    
                self._human_delay(5, 10) # Delay between keywords
                
            browser.close()
            
        return jobs_found
