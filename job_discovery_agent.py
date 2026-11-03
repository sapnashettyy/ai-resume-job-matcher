import requests
import re
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


def role_family(query):
    """Map the selected search role to a focused family of related job titles."""
    q = (query or "").lower()
    if any(x in q for x in ("backend", "back-end", "back end", "api developer", "server-side", "server side")):
        return "backend"
    if any(x in q for x in ("frontend", "front-end", "front end", "ui developer")):
        return "frontend"
    if any(x in q for x in ("web developer", "web development")):
        return "web"
    if any(x in q for x in ("data analyst", "business analyst")):
        return "data_analyst"
    if any(x in q for x in ("machine learning", "ml engineer", "ai engineer", "applied ai")):
        return "ml"
    if any(x in q for x in ("java developer", "java engineer")):
        return "java"
    if any(x in q for x in ("python developer", "python engineer")):
        return "python"
    if any(x in q for x in ("full stack", "full-stack", "fullstack")):
        return "fullstack"
    if any(x in q for x in ("software engineer", "software developer")):
        return "software"
    return "general"


def role_relevance(query, title, description):
    """Return 0 for unrelated roles; higher scores indicate closer title matches."""
    family = role_family(query)
    t = (title or "").lower()
    d = (description or "").lower()

    if family == "backend":
        if any(x in t for x in ("machine learning", "data scientist", "data analyst",
                                "ai engineer", "frontend", "front-end", "web designer")):
            return 0
        if any(x in t for x in ("backend", "back-end", "back end", "api developer",
                                "server-side", "server side")):
            return 4
        if any(x in t for x in ("software engineer", "software developer", "platform engineer")):
            return 3 if any(x in d for x in ("backend", "back-end", "rest api", "server-side", "server side", "api development")) else 0
        return 0
    if family == "frontend":
        if any(x in t for x in ("backend", "back-end", "machine learning", "data analyst", "data scientist")):
            return 0
        if any(x in t for x in ("frontend", "front-end", "front end", "ui developer")):
            return 4
        if "web developer" in t:
            return 3
        if any(x in t for x in ("software engineer", "software developer")) and any(x in d for x in ("javascript", "react", "frontend", "front-end", "css")):
            return 2
        return 0
    if family == "web":
        if any(x in t for x in ("machine learning", "data analyst", "data scientist", "devops")):
            return 0
        if any(x in t for x in ("web developer", "frontend", "front-end", "front end", "full stack", "full-stack", "fullstack")):
            return 4
        if any(x in t for x in ("software engineer", "software developer")) and any(x in d for x in ("html", "css", "javascript", "react", "web application")):
            return 2
        return 0
    if family == "data_analyst":
        return 4 if any(x in t for x in ("data analyst", "business analyst", "bi analyst", "reporting analyst")) else 0
    if family == "ml":
        return 4 if any(x in t for x in ("machine learning", "ml engineer", "ai engineer", "applied ai", "data scientist")) else 0
    if family == "java":
        return 4 if "java" in t and any(x in t for x in ("developer", "engineer", "programmer")) else 0
    if family == "python":
        if "python" in t and any(x in t for x in ("developer", "engineer", "programmer")):
            return 4
        if any(x in t for x in ("software engineer", "software developer")) and "python" in d:
            return 2
        return 0
    if family == "fullstack":
        return 4 if any(x in t for x in ("full stack", "full-stack", "fullstack")) else 0
    if family == "software":
        return 4 if any(x in t for x in ("software engineer", "software developer")) else 0
    # For an unrecognized search phrase, require the main query terms in title.
    terms = [x for x in re.findall(r"[a-z0-9+#.]+", (query or "").lower())
             if x not in {"intern", "internship", "junior", "fresher", "entry", "level", "developer", "engineer"}]
    return 2 if terms and any(term in t for term in terms) else 0


def location_priority(location, description="", remote=False):
    """Rank confirmed India locations above remote/unknown listings."""
    loc = (location or "").lower()
    if any(term in loc for term in INDIA_TERMS):
        return 3
    if any(term in loc for term in ("worldwide", "anywhere", "global")):
        return 2
    if remote or "remote" in loc:
        return 1
    return 0


def india_eligibility_status(location, description=""):
    """Only claim India eligibility when location text explicitly supports it."""
    loc = (location or "").lower()
    desc = (description or "").lower()
    if any(term in loc for term in INDIA_TERMS):
        return "India location listed; confirm specific hiring requirements."
    if any(term in loc for term in ("worldwide", "anywhere", "global")):
        return "Worldwide eligibility appears to be stated; verify the listing."
    if any(term in desc for term in ("candidates based in india", "applicants in india", "india only", "must be located in india")):
        return "India eligibility explicitly mentioned; verify the listing."
    if any(term in loc for term in ("canada", "united states", "usa", "uk", "united kingdom", "europe", "germany")):
        return "Location restriction may apply; India eligibility not confirmed."
    if "remote" in loc or "remote" in desc:
        return "Remote role; eligibility for applicants in India is unknown."
    return "Applicant location eligibility is not verified."


def filter_and_rank_jobs(jobs, max_results=20, query=None):
    """Filter entry-level jobs by the selected role, then rank by relevance/location."""
    unique_jobs = {}
    entry_terms = [
        "intern", "internship", "junior", "graduate", "entry level",
        "entry-level", "fresher", "trainee", "new grad", "new graduate",
        "apprentice", "early career", "associate", "co-op", "coop",
    ]
    senior_terms = [
        "senior", "sr.", "staff", "principal", "director", "manager",
        "head of", "chief", "architect", "lead engineer",
    ]

    for original in jobs:
        job = dict(original)
        title = text_value(job.get("title")).strip()
        description = text_value(job.get("description"))
        location = text_value(job.get("location"))
        url = text_value(job.get("url")).strip()
        title_lower = title.lower()

        if not title or not url.startswith(("https://", "http://")):
            continue
        if any(term in title_lower for term in senior_terms):
            continue
        if not is_technical_role(title):
            continue

        entry_in_title = any(term in title_lower for term in entry_terms)
        desc_lower = description.lower()
        entry_in_description = any(term in desc_lower for term in [
            "entry-level", "entry level", "new graduate", "recent graduate",
            "no experience required", "0-2 years", "0–2 years", "0 to 2 years",
            "0-1 years", "fresh graduates", "internship", "intern role",
            "students are welcome", "graduate role",
        ])

        # First enforce role relevance. Do not reject a relevant junior-looking
        # listing merely because the API omitted its seniority metadata.
        relevance = role_relevance(query, title, description) if query else 1
        if relevance <= 0:
            continue
        if url in unique_jobs:
            # Keep the more relevant version of a duplicate URL.
            if relevance <= unique_jobs[url].get("role_relevance", 0):
                continue

        job["description"] = description[:1200]
        job["role_relevance"] = relevance
        job["entry_level_signal"] = bool(entry_in_title or entry_in_description)
        job["seniority_note"] = (
            "Entry-level signal found in listing."
            if job["entry_level_signal"]
            else "Seniority not clearly stated; verify requirements before applying."
        )
        job["location_priority"] = location_priority(location, description, job.get("remote", False))
        job["india_eligibility_status"] = india_eligibility_status(location, description)
        unique_jobs[url] = job

    results = list(unique_jobs.values())
    results.sort(key=lambda job: (
        job.get("entry_level_signal", False),
        job.get("role_relevance", 0),
        job.get("location_priority", 0),
    ), reverse=True)
    return results[:max_results]


def build_search_links(query="software engineer intern"):
    """Create search links targeted to the selected role."""
    role = (query or "software engineer intern").strip()
    searches = [
        (f"{role} jobs in India", f"{role} jobs India"),
        (f"{role} internships in India", f"{role} internship India"),
        (f"Entry-level {role} roles", f"{role} fresher OR junior OR entry-level India"),
        (f"Remote {role} roles", f"remote {role} internship OR junior worldwide"),
        (f"{role} on LinkedIn", f"site:linkedin.com/jobs/view {role} India"),
    ]
    return [
        {"source": "Google", "title": title,
         "url": "https://www.google.com/search?q=" + quote_plus(search_query)}
        for title, search_query in searches
    ]


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
        query=query,
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

    family = role_family(query)
    # Search several close variants so a job board's exact-title matching does
    # not cause an empty result. Final filtering still enforces role relevance.
    query_variants = list(dict.fromkeys([
        query,
        f"{query} intern",
        f"{query} junior",
        f"{query} entry level",
    ]))
    tasks = []
    for index, search_term in enumerate(query_variants):
        tasks.append((f"Himalayas [{search_term}]", lambda term=search_term: fetch_himalayas(term)))
        tasks.append((f"Remotive [{search_term}]", lambda term=search_term: fetch_remotive(term)))
    tasks.extend([
        ("Arbeitnow", fetch_arbeitnow),
        ("Remotive general entry-level", lambda: fetch_remotive(f"{family} intern")),
    ])
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

    jobs = filter_and_rank_jobs(all_jobs, max_results=max_results, query=query)
    return {
        "jobs": jobs,
        "search_links": build_search_links(query),
        "errors": errors,
    }
