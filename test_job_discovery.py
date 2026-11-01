
from job_discovery_agent import search_jobs

if __name__ == "__main__":
    query = "software engineer intern"

    print("\nSearching job sources...\n")

    result = search_jobs(query, max_results=20)

    print("\n=== MATCHING JOB LISTINGS ===\n")

    if result["jobs"]:
        for index, job in enumerate(result["jobs"], start=1):
            print(f"{index}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Remote eligibility: {job.get('remote_eligibility', 'Not available')}")
            print(f"   Source: {job['source']}")
            print(f"   URL: {job['url']}")
            print()
    else:
        print("No matching listings returned by the APIs.")

    print("\n=== SOURCE ERRORS ===\n")

    if result["errors"]:
        for error in result["errors"]:
            print(error)
    else:
        print("No API errors reported.")

    print("\n=== EXTERNAL JOB SEARCH LINKS ===\n")

    for link in result["search_links"]:
        print(f"{link['source']}: {link['title']}")
        print(link["url"])
        print()
