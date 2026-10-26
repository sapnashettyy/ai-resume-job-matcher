
from llm_analyzer import analyze_resume


resume = """
Entry-level Python developer.
Skills: Python, SQL, Git, GitHub, pandas, and NumPy.
Built a student performance analysis project using pandas.
Currently learning FastAPI.
"""


job_description = """
Junior Python Developer

Required skills:
- Python
- SQL
- Git and GitHub
- REST APIs
- Problem-solving and debugging

Preferred skills:
- FastAPI
- pytest
- Docker
- pandas and NumPy
"""


try:
    result = analyze_resume(resume, job_description)

    for section, items in result.items():
        print(f"\n{section.replace('_', ' ').title()}:")

        for item in items:
            print(f"- {item}")

except Exception as error:
    print(f"Analysis failed: {error}")
