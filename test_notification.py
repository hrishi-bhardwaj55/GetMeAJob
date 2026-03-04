from scout import Job
from notifier import NotifierAgent
import config

def send_test():
    # Create a dummy job to showcase the format
    dummy_job = Job(
        job_id="123456789",
        title="Senior Software Engineer - AI Systems",
        company="TechNova Solutions",
        location="Remote, USA",
        application_link="https://www.linkedin.com/jobs/view/test",
        salary="$150,000 / yr",
        description="We are looking for an experienced software engineer to build intelligent agentic workflows using Python. Experience with LLMs, prompt engineering, and API integration is highly desired. This role involves designing scalable architectures and working with data pipelines."
    )
    
    print("Initializing test Webhook...")
    test_webhook = config.JOB_PROFILES[0].get("webhook_url", "")
    notifier = NotifierAgent(webhook_url=test_webhook, bot_name="Test Engineering Bot")
    result = notifier.send_notification(dummy_job)
    if result:
        print("Success! Check your Discord channel.")
    else:
        print("Failed to send.")

if __name__ == "__main__":
    send_test()
