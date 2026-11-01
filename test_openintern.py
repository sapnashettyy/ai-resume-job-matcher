
import requests

API_URL = "https://openintern.dev/api/v1/jobs"

TECH_TERMS = [
    "software", "python", "java", "backend", "frontend",
    "full stack", "full-stack", "data engineer", "data analyst",
    "data scientist", "machine learning", "ai engineer",
    "devops", "cloud engineer", "qa engineer", "automation",
    "cybersecurity", "web developer", "developer", "programmer",
]

ENTRY_TERMS = [
    "intern", "internship", "junior", "graduate",
    "entry level", "entry-level", "fresher", "trainee",
    "new grad", "apprentice", "associate",
]


def fetch_india_jobs():
    params = {
        "role": "software,backend,frontend,fullstack,data,ml,devops",
        "limit": 100,
    }

    try:
        response = requests.get(API_URL, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as error:
        print("API error:", error)
        return []

    families = data.get("jobs", [])
    results = []
    seen_urls = set()

    for family in families:
        title = str(family.get("title") or "").strip()
        company_data = family.get("company") or {}
        company = (
            company_data.get("name", "Not specified")
            if isinstance(company_data, dict)
            else str(company_data)
        )

        title_lower = title.lower()

        if not any(term in title_lower for term in TECH_TERMS):
            continue

        if not any(term in title_lower for term in ENTRY_TERMS):
            continue

        for posting in family.get("postings", []):
            location = str(posting.get("location") or "").strip()
            location_lower = location.lower()

            # Only prioritize postings explicitly located in India.
            if not any(
                country in location_lower
                for country in ["india", "mumbai", "bangalore",
                                "bengaluru", "hyderabad", "pune",
                                "chennai", "noida", "gurugram",
                                "gurgaon", "new delhi"]
            ):
                continue

            apply_url = str(
                posting.get("apply_url")
                or posting.get("url")
                or ""
            ).strip()

            if not apply_url.startswith("https://"):
                continue

            if apply_url in seen_urls:
                continue

            seen_urls.add(apply_url)

            results.append({
                "title": title,
                "company": company,
                "location": location,
                "url": apply_url,
            })

    return results


if __name__ == "__main__":
    jobs = fetch_india_jobs()
    print(f"\nIndia-focused results: {len(jobs)}")

    for index, job in enumerate(jobs, start=1):
        print(f"\n{index}. {job['title']}")
        print("Company:", job["company"])
        print("Location:", job["location"])
        print("Apply:", job["url"])
