import requests
from urllib.parse import quote_plus

ARBEITNOW_API = "https://www.arbeitnow.com/api/job-board-api"
REMOTIVE_API = "https://remotive.com/api/remote-jobs"
TIMEOUT = 20

# Roles suitable for computer science freshers
TECH_TERMS = [
    "software engineer",
    "software developer",
    "python developer",
    "backend developer",
    "back end developer",
    "machine learning engineer",
    "machine learning",
    "ai engineer",
    "artificial intelligence",
    "data analyst",
    "data scientist",
    "data engineer",
    "ml engineer",
    "web developer",
    "full stack developer",
    "fullstack developer",
    "devops engineer",
    "qa engineer",
    "test engineer",
    "java developer",
    "frontend developer",
    "front end developer",
]

ENTRY_TERMS = [
    "intern",
    "internship",
    "junior",
    "graduate",
    "entry level",
    "entry-level",
    "fresher",
    "trainee",
    "new grad",
    "new graduate",
    "apprentice",
    "early career",
    "associate",
]

SENIOR_TERMS = [
    "senior",
    "sr.",
    "staff engineer",
    "principal",
    "director",
    "manager",
    "head of",
    "lead engineer",
    "chief ",
    "architect",
]

INDIA_TERMS = [
    "india", "bengaluru", "bangalore", "mangalore",
    "mangaluru", "mumbai", "pune", "hyderabad",
    "chennai", "delhi", "noida", "gurugram",
    "gurgaon", "kolkata", "kochi", "ahmedabad",
]

REMOTE_TERMS = [
    "remote", "worldwide", "work from home", "anywhere"
]


def text_value(value):
    """Convert API values into safe searchable text."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(text_value(item) for item in value)
    if isinstance(value, dict):
        return " ".join(text_value(item) for item in value.values())
    return ""


def is_technical_role(title):
    title = title.lower()
    return any(term in title for term in TECH_TERMS)


def is_senior_role(title):
    title = title.lower()
    return any(term in title for term in SENIOR_TERMS)


def has_entry_level_signal(title, description=""):
    text = f"{title} {description}".lower()
    return any(term in text for term in ENTRY_TERMS)


def location_priority(location, description="", remote=False):
    """Prioritize India-based roles, then remote roles, then other locations."""
    location_text = location.lower()
    combined = f"{location_text} {description.lower()}"

    if any(term in location_text for term in INDIA_TERMS):
        return 3

    if remote or any(term in combined for term in REMOTE_TERMS):
        return 2

    return 1


def fetch_arbeitnow():
    """Fetch public listings from Arbeitnow."""
    response = requests.get(ARBEITNOW_API, timeout=TIMEOUT)
    response.raise_for_status()

    data = response.json()
    jobs = []

    for item in data.get("data", []):
        title = text_value(item.get("title")).strip()
        url = text_value(item.get("url")).strip()

        if not title or not url:
            continue

        jobs.append({
            "title": title,
            "company": (
                text_value(item.get("company_name")) or "Not specified"
            ),
            "location": (
                text_value(item.get("location")) or "Not specified"
            ),
            "description": text_value(item.get("description")),
            "url": url,
            "source": "Arbeitnow",
            "remote": bool(item.get("remote", False)),
        })

    return jobs


def fetch_remotive(query):
    """Fetch remote jobs matching a search query."""
    response = requests.get(
        REMOTIVE_API,
        params={"search": query},
        timeout=TIMEOUT,
    )
    response.raise_for_status()

    data = response.json()
    jobs = []

    for item in data.get("jobs", []):
        title = text_value(item.get("title")).strip()
        url = text_value(item.get("url")).strip()

        if not title or not url:
            continue

        jobs.append({
            "title": title,
            "company": (
                text_value(item.get("company_name")) or "Not specified"
            ),
            "location": (
                text_value(item.get("candidate_required_location")) or "Remote"
            ),
            "description": text_value(item.get("description")),
            "url": url,
            "source": "Remotive",
            "remote": True,
        })

    return jobs


def fetch_himalayas(query="software engineer intern"):
    """Fetch jobs using the official Himalayas search API."""
    url = "https://himalayas.app/jobs/api/search"

    response = requests.get(
        url,
        params={"q": query},
        timeout=TIMEOUT,
    )
    response.raise_for_status()

    data = response.json()
    items = data.get("jobs", [])
    jobs = []

    for item in items:
        title = text_value(item.get("title")).strip()
        company = text_value(item.get("companyName")).strip()
        description = text_value(
            item.get("description") or item.get("excerpt")
        )
        application_url = text_value(item.get("applicationLink")).strip()

        if not title or not application_url.startswith("http"):
            continue

        restrictions = item.get("locationRestrictions") or []
        location_names = [
            text_value(place.get("name")).strip()
            for place in restrictions
            if isinstance(place, dict) and place.get("name")
        ]

        if location_names:
            location = ", ".join(location_names)
            remote_eligibility = "Restricted"
        else:
            location = "Remote — eligibility not verified"
            remote_eligibility = "Unknown"

        seniority = text_value(item.get("seniority"))
        employment_type = text_value(item.get("employmentType"))

        jobs.append({
            "title": title,
            "company": company or "Not specified",
            "location": location,
            "description": (
                f"{description} "
                f"Seniority: {seniority}. "
                f"Employment type: {employment_type}."
            ),
            "url": application_url,
            "source": "Himalayas",
            "remote": True,
            "remote_eligibility": remote_eligibility,
        })

    return jobs


def filter_and_rank_jobs(jobs, max_results=20):
    """Filter technical jobs while keeping likely entry-level roles."""
    unique_jobs = {}
    rejected_senior = 0
    rejected_technical = 0
    rejected_entry = 0

    entry_terms = [
        "intern", "internship", "junior", "graduate",
        "entry level", "entry-level", "fresher",
        "trainee", "new grad", "new graduate",
        "apprentice", "early career", "associate",
    ]

    senior_terms = [
        "senior", "sr.", "staff", "principal",
        "director", "manager", "head of",
        "chief", "architect",
    ]

    for job in jobs:
        title = text_value(job.get("title")).strip()
        description = text_value(job.get("description"))
        location = text_value(job.get("location"))
        url = text_value(job.get("url")).strip()
        title_lower = title.lower()

        if not title or not url.startswith("https://"):
            continue

        # Always exclude clearly senior roles.
        if any(term in title_lower for term in senior_terms):
            rejected_senior += 1
            continue

        if not is_technical_role(title):
            rejected_technical += 1
            continue

        # Accept explicit entry-level titles or descriptions.
        description_lower = description.lower()
        entry_in_title = any(
            term in title_lower for term in entry_terms
        )
        entry_in_description = any(
            term in description_lower
            for term in [
                "entry-level", "entry level", "new graduate",
                "recent graduate", "no experience required",
                "0-2 years", "0–2 years", "0 to 2 years",
                "0-1 years", "fresh graduates",
            ]
        )

        if not (entry_in_title or entry_in_description):
            rejected_entry += 1
            continue

        if url in unique_jobs:
            continue

        job["description"] = description[:1200]
        job["location_priority"] = location_priority(
            location,
            description,
            job.get("remote", False),
        )
        unique_jobs[url] = job

    results = list(unique_jobs.values())
    results.sort(
        key=lambda job: job["location_priority"],
        reverse=True,
    )

    print("Rejected senior:", rejected_senior)
    print("Rejected non-technical:", rejected_technical)
    print("Rejected non-entry-level:", rejected_entry)
    print("Accepted:", len(results))

    return results[:max_results]


def build_search_links(query="software engineer intern"):
    """Create targeted searches for India-based entry-level jobs."""
    searches = [
        (
            "Internships in India",
            "site:linkedin.com/jobs/view software engineer internship India",
        ),
        (
            "Python fresher jobs",
            "Python developer fresher jobs India",
        ),
        (
            "Machine Learning internships",
            "machine learning internship India 2026",
        ),
        (
            "Data Analyst fresher jobs",
            "data analyst fresher jobs India",
        ),
        (
            "Graduate software jobs",
            "graduate software developer jobs India",
        ),
        (
            "Remote internships",
            "remote software engineering internship worldwide",
        ),
    ]

    links = []
    for title, search_query in searches:
        links.append({
            "source": "Google",
            "title": title,
            "url": "https://www.google.com/search?q=" + quote_plus(search_query),
        })

    return links


def search_jobs(query="software engineer intern", max_results=20):
    """Fetch, filter and rank jobs from available public APIs."""
    all_jobs = []
    errors = []

    # Define queries before using them in the Remotive loop.
    search_queries = [
        query,
        "software engineer intern India",
        "software developer fresher India",
        "python developer fresher India",
        "data analyst intern India",
        "machine learning intern India",
        "AI engineer intern India",
        "graduate software developer India",
        "junior data scientist India",
        "remote software engineering intern",
    ]

    # Fetch jobs from Himalayas.
    try:
        himalayas_jobs = fetch_himalayas(query)
        print(f"Himalayas fetched: {len(himalayas_jobs)}")
        all_jobs.extend(himalayas_jobs)
    except (requests.RequestException, ValueError, KeyError) as error:
        errors.append(f"Himalayas: {error}")

    # Fetch available jobs from Arbeitnow.
    try:
        arbeitnow_jobs = fetch_arbeitnow()
        print(f"Arbeitnow fetched: {len(arbeitnow_jobs)}")
        all_jobs.extend(arbeitnow_jobs)
    except (requests.RequestException, ValueError, KeyError) as error:
        errors.append(f"Arbeitnow: {error}")

    # Search Remotive with multiple queries; duplicates are removed later.
    for search_term in dict.fromkeys(search_queries):
        try:
            remotive_jobs = fetch_remotive(search_term)
            print(
                f"Remotive [{search_term}]: "
                f"{len(remotive_jobs)} fetched"
            )
            all_jobs.extend(remotive_jobs)
        except (requests.RequestException, ValueError, KeyError) as error:
            errors.append(f"Remotive [{search_term}]: {error}")

    print(f"Total raw records: {len(all_jobs)}")

    filtered_jobs = filter_and_rank_jobs(
        all_jobs,
        max_results=max_results,
    )

    print(f"Unique matching jobs: {len(filtered_jobs)}")

    return {
        "jobs": filtered_jobs,
        "search_links": build_search_links(query),
        "errors": errors,
    }


def search_jobs_fast(query="python developer intern", max_results=12):
    """Search a few public job sources concurrently to keep the UI responsive."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    tasks = [
        ("Himalayas", lambda: fetch_himalayas(query)),
        ("Arbeitnow", fetch_arbeitnow),
        ("Remotive", lambda: fetch_remotive(query)),
        ("Remotive India", lambda: fetch_remotive("software engineer intern India")),
    ]
    all_jobs = []
    errors = []
    with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        future_sources = {executor.submit(fn): name for name, fn in tasks}
        for future in as_completed(future_sources):
            source = future_sources[future]
            try:
                all_jobs.extend(future.result())
            except Exception as error:
                errors.append(f"{source}: {error}")

    jobs = filter_and_rank_jobs(all_jobs, max_results=max_results)
    return {
        "jobs": jobs,
        "search_links": build_search_links(query),
        "errors": errors,
    }
