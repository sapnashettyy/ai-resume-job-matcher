
import requests

API_URL = "https://internscan.vercel.app/in/api/active.json"

try:
    response = requests.get(API_URL, timeout=20)
    print("Status:", response.status_code)
    response.raise_for_status()

    data = response.json()

    print("Response type:", type(data).__name__)

    if isinstance(data, dict):
        print("Top-level keys:", list(data.keys()))
        jobs = data.get("jobs", data.get("data", []))

        if isinstance(jobs, list):
            print("Jobs received:", len(jobs))

            for job in jobs[:5]:
                print("\n--- JOB ---")
                print(job)
        else:
            print("Sample response:", str(data)[:2000])

    elif isinstance(data, list):
        print("Jobs received:", len(data))

        for job in data[:5]:
            print("\n--- JOB ---")
            print(job)

    else:
        print("Unexpected response:", str(data)[:2000])

except (requests.RequestException, ValueError) as error:
    print("API test failed:", error)
