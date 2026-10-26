
from pathlib import Path
from resume_parser import extract_resume_text

pdf_path = Path("AI_resume_week_1.pdf")

if not pdf_path.exists():
    print("Test PDF not found. Check the filename.")
else:
    file_bytes = pdf_path.read_bytes()

    extracted_text = extract_resume_text(
        pdf_path.name,
        file_bytes
    )

    print("Text extracted successfully!")
    print(extracted_text[:500])
