import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

class NotifierAgent:
    def __init__(self):
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT
        self.sender_email = config.SENDER_EMAIL
        self.sender_password = config.SENDER_PASSWORD
        self.receiver_email = config.RECEIVER_EMAIL

    def send_notification(self, job):
        """Sends an email notification with job details."""
        if self.sender_email == "YOUR_EMAIL@gmail.com" or self.receiver_email == "YOUR_RECEIVER_EMAIL@domain.com":
            print(f"[Notifier Agent] Email settings not configured. Cannot send notification for: {job.title}")
            return False

        print(f"[Notifier Agent] Sending Email for {job.title} to {self.receiver_email}...")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = self.receiver_email
        msg['Subject'] = f"New Job Match: {job.title} at {job.company}"

        # Create HTML Body
        desc_snippet = job.description[:500] + "..." if len(job.description) > 500 else job.description
        html = f"""
        <html>
          <body>
            <h2>Job Match: <a href="{job.application_link}">{job.title}</a></h2>
            <p><strong>Company:</strong> {job.company}</p>
            <p><strong>Location:</strong> {job.location}</p>
            <p><strong>Salary:</strong> {job.salary}</p>
            <br>
            <p><strong>Description Snippet:</strong></p>
            <p><i>{desc_snippet}</i></p>
            <br>
            <p>Job ID: {job.job_id}</p>
            <p><a href="{job.application_link}"><strong>Apply Here</strong></a></p>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))

        try:
            # Connect and authenticate
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls() 
            server.login(self.sender_email, self.sender_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.sender_email, self.receiver_email, text)
            server.quit()
            
            print("[Notifier Agent] Email sent successfully.")
            return True
        except Exception as e:
            print(f"[Notifier Agent] Failed to send email. Error: {e}")
            return False
