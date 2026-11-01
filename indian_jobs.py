
import requests


API_URL = "https://locojob.com/api/public/v1/jobs"

TIMEOUT = 20

TECH_TERMS = [
    "software", "python", "machine learning", "artificial intelligence",
    "ai engineer", "data analyst", "data scientist", "data engineer",
    "java developer", "web developer", "backend", "frontend",
    "full stack", "full-stack", "devops", "qa engineer",
    "automation tester", "cybersecurity", "cloud engineer",
]

ENTRY_TERMS = [
    "intern", "internship", "junior", "graduate",
    "entry level", "entry-level", "fresher", "trainee",
    "new grad", "apprentice", "associate",
]


def fetch_indian_jobs(query="python developer"):
    params = {
        "q": query,
        "page": 1,
        "per_page": 20,
    }

    try:
        response = requests.get(
            API_URL, params=params, timeout=TIMEOUT
        )

        print("API status:", response.status_code)

        if not response.ok:
            print("API response:", response.text)

        response.raise_for_status()
        data = response.json()

    except (requests.RequestException, ValueError) as error:
        print(f"LocoJobs API error: {error}")
        return []

    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get("jobs", data.get("results", []))
    else:
        items = []

    print("Raw jobs received:", len(items))
    for item in items:
     print(
        "TITLE:", item.get("title"),
        "| COMPANY:", item.get("company"),
        "| LOCATION:", item.get("location")
    )

    jobs = []
    seen_urls = set()

    for item in items:
        if not isinstance(item, dict):
            continue

        title = str(item.get("title") or "").strip()
        description = str(item.get("description") or "")
        searchable = f"{title} {description}".lower()

        # Keep technical jobs, but don't require internship wording
        # in the title itself.
        if not any(term in title.lower() for term in TECH_TERMS):
            continue

        if not any(term in searchable for term in ENTRY_TERMS):
            continue

        location_data = item.get("location") or {}

        if isinstance(location_data, dict):
            city = location_data.get("city", "")
            state = location_data.get("state", "")
            country = location_data.get("country", "")
            location = ", ".join(
                str(part) for part in [city, state, country] if part
            )
            is_remote = bool(location_data.get("remote", False))
        else:
            location = str(location_data)
            is_remote = bool(item.get("remote", False))

        company_data = item.get("company") or {}

        if isinstance(company_data, dict):
            company = company_data.get("name", "Not specified")
        else:
            company = str(company_data or "Not specified")

        job_url = str(
            item.get("apply_url") or item.get("url") or ""
        ).strip()

        if not job_url.startswith("https://") or job_url in seen_urls:
            continue

        seen_urls.add(job_url)

        jobs.append({
            "title": title,
            "company": company,
            "location": location or "Not specified",
            "description": description[:1200],
            "url": job_url,
            "source": "LocoJobs",
            "remote": is_remote,
            "remote_eligibility": "Verify on original listing",
        })

    print("Technical entry-level jobs after filtering:", len(jobs))
    return jobs
