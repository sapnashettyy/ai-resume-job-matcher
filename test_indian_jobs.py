
from indian_jobs import fetch_indian_jobs

jobs = fetch_indian_jobs("software engineer intern")

print(f"India-focused results: {len(jobs)}")

for job in jobs[:10]:
    print("-" * 50)
    print("Title:", job["title"])
    print("Company:", job["company"])
    print("Location:", job["location"])
    print("URL:", job["url"])
