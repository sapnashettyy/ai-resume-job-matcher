# AI Resume Analyzer and Job-Matching Agent
## Project Overview
This project aims to develop an AI-powered application that analyzes a candidate's resume against a job description. It identifies matching skills, highlights skill gaps, calculates a transparent match score, and suggests improvements to help candidates prepare for job applications.
## Problem Statement
Candidates often find it difficult to determine how well their resumes match job requirements. Manually comparing skills and identifying missing qualifications can be time-consuming.
## Objectives
- Extract text from PDF and DOCX resumes.
- Identify skills mentioned in resumes and job descriptions.
- Calculate a transparent resume-to-job match score.
- Highlight matched and missing skills.
- Provide truthful, actionable resume improvement suggestions.
- Help candidates identify skills they may need to learn.
## Planned Features
- Resume upload and text extraction
- Job description analysis
- Skill matching and gap analysis
- Match score calculation
- AI-generated improvement suggestions
- User-friendly web interface
## Planned Technology Stack
- Python
- Streamlit
- Large Language Model (LLM) API
- PyMuPDF
- python-docx
- pytest
- Git and GitHub
## How the System Will Work
1. Upload a resume.
2. Enter a job description.
3. Extract and analyze the text.
4. Identify required and resume-supported skills.
5. Calculate the match score using Python.
6. Display matching skills, skill gaps, and suggestions.
## Match Score
The planned score is calculated as:
Match Score = (Matched Required Skills / Total Distinct Required Skills) × 100
This score measures skill alignment with the supplied job description. It does not predict the probability of getting hired.
## Responsible AI
The application will avoid inventing qualifications or work experience. It will distinguish supported skills from skills that are missing or require verification. Uploaded documents will be treated as untrusted input.
## Project Status
Week 1: Planning, requirements analysis, workflow design, and test-case preparation.

Implementation and testing are planned for subsequent weeks.

## Author
Name: Sapna

## License
To be decided.
