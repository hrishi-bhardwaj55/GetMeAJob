# Use the official Microsoft Playwright image which includes all browser dependencies
FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Environment Variables that can be overridden at runtime
# ENV SEARCH_KEYWORDS="Software Engineer"
# ENV DISCORD_WEBHOOK_URL="your_webhook_here"

# Set the entrypoint to run the main script
CMD ["python", "main.py"]
