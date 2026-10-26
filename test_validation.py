from pathlib import Path
from resume_parser import extract_resume_text

# Test 1: Unsupported file type
try:
    extract_resume_text("resume.txt", b"Sample resume text")
    print("Test failed: No error was raised.")

except ValueError as error:
    print("Unsupported file test passed:", error)


# Test 2: Empty PDF
pdf_path = Path("empty_resume.pdf")

try:
    file_bytes = pdf_path.read_bytes()

    extract_resume_text(pdf_path.name, file_bytes)

    print("Test failed: Empty PDF was accepted.")

except ValueError as error:
    print("Empty PDF test passed:", error)


print("Validation tests completed.")