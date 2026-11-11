import html
import hashlib

import json

import re

import time

import streamlit as st

from resume_parser import extract_resume_text

from llm_analyzer import analyze_resume, generate_job_keywords, generate_skill_to_role_pathways
from job_discovery_agent import search_jobs_fast

# --------------------------------------------------

# PAGE CONFIGURATION

# --------------------------------------------------

st.set_page_config(

          page_title="TalentLens AI",

          page_icon="✦",

          layout="wide",

          initial_sidebar_state="expanded",

)

# --------------------------------------------------

# CUSTOM STYLING

# --------------------------------------------------

st.markdown(

          """

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root {
  --bg: #F4F3F0;
  --panel: #FFFFFF;
  --border: #E5E3DE;
  --text: #191919;
  --muted: #555650;
  --purple: #6557D9;
  --green: #16845D;
  --red: #C34C5B;
  --yellow: #9A7414;
}
.stApp {
  background: radial-gradient(ellipse at 75% 0%, #FFFFFF 0%, transparent 45%), var(--bg);
  color: var(--text);
  font-family: 'Inter', sans-serif;
}

section[data-testid="stSidebar"] { background: #F0EFEC; border-right: 1px solid #D8D6D0; min-width: 265px; }
section[data-testid="stSidebar"] .block-container { padding: 1.5rem 1rem 2rem; }
section[data-testid="stSidebar"] [data-testid="stRadio"] > label { color:#45443F !important; font-size:.72rem !important; font-weight:800 !important; letter-spacing:1.5px; }
section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] { gap:.35rem; }
section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label { color:#242424 !important; font-weight:650 !important; padding:.62rem .7rem; border-radius:10px; transition:background .15s ease; }
section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover { background:#E3E1DC; }
section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) { background:#191919; color:#FFFFFF !important; }
section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p { color:#FFFFFF !important; }
section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label p { color:inherit !important; }
section[data-testid="stSidebar"] [data-testid="stFileUploader"] { background:#FFFFFF; }
.sidebar-foot { color:#252525; font-weight:700; line-height:1.7; font-size:.86rem; }
.sidebar-foot span { color:#555650; font-weight:400; font-size:.78rem; }
.dashboard-title { font-size:clamp(2.2rem,4vw,3.4rem); font-weight:800; line-height:1.08; letter-spacing:-2px; margin-top:1.5rem; color:#191919; }
.dashboard-title span, .page-title span { color:#555650; }
.page-title { font-size:clamp(2.2rem,4vw,3.2rem); font-weight:800; line-height:1.08; letter-spacing:-1.8px; margin-top:1.3rem; margin-bottom:.55rem; }
.dashboard-subtitle { color:#555650; font-size:1rem; margin:.8rem 0 1.7rem; max-width:760px; }
.metric-top { display:flex; justify-content:space-between; align-items:center; color:#555650; font-size:.68rem; letter-spacing:1.1px; font-weight:700; }
.metric-top b { background:#F1F0ED; color:#242424; border-radius:50%; width:28px; height:28px; display:flex; align-items:center; justify-content:center; font-size:1rem; }
.dashboard-metric { min-height:148px; }
.dashboard-metric .metric-value { font-size:1.8rem; margin-top:.9rem; }
.metric-note { color:#5D5D57; font-size:.72rem; margin-top:.35rem; }
.section-heading { font-size:1.1rem; font-weight:800; margin:1.9rem 0 .9rem; letter-spacing:-.3px; }
.feature-card { min-height:210px; background:#FFFFFF; border:1px solid #E5E3DE; border-radius:20px; padding:1.35rem; box-shadow:0 8px 24px rgba(24,24,24,.035); }
.feature-card-dark { background:#171717; color:#FFFFFF; border-color:#171717; }
.feature-kicker { font-size:.68rem; font-weight:700; letter-spacing:1.4px; color:#5D5D57; margin-bottom:1.3rem; }
.feature-card-dark .feature-kicker { color:#B7B4AC; }
.feature-title { font-size:1.55rem; line-height:1.16; font-weight:800; letter-spacing:-.8px; }
.feature-copy { color:#555650; font-size:.86rem; line-height:1.55; margin-top:.85rem; }
.feature-card-dark .feature-copy { color:#C8C7C2; }
.quick-card { background:rgba(255,255,255,.8); border:1px solid #E5E3DE; border-radius:16px; padding:1rem; min-height:140px; }
.quick-card b { display:block; margin:.65rem 0 .3rem; font-size:.9rem; }
.quick-card p { color:#555650; font-size:.78rem; line-height:1.5; margin:0; }
.quick-icon { background:#F0EFEB; border-radius:10px; width:34px; height:34px; display:flex; align-items:center; justify-content:center; font-size:1.2rem; font-weight:700; }

.block-container { max-width: 1320px; padding-top: 1.5rem; padding-bottom: 3rem; }
header[data-testid="stHeader"] { background: rgba(244,243,240,0.85); }
#MainMenu, footer { visibility: hidden; }
.brand { font-size: 1.55rem; font-weight: 800; letter-spacing: -0.8px; color: var(--text); }
.brand span, .accent { color: var(--purple); }
.eyebrow { color: #555650; font-size: 0.72rem; font-weight: 700; letter-spacing: 2.2px; text-transform: uppercase; }
.hero-title { font-size: clamp(2.5rem, 5vw, 4.25rem); font-weight: 800; letter-spacing: -2.8px; line-height: 1.04; color: var(--text); margin: 0.9rem 0; }
.hero-title span { color: var(--purple); }
.feature { color: #555650; font-size: 0.9rem; padding: 0.7rem 0; }
.panel { background: rgba(255,255,255,0.9); border: 1px solid var(--border); border-radius: 18px; padding: 1.2rem 1.25rem; margin-bottom: 0.65rem; box-shadow: 0 8px 24px rgba(24,24,24,0.035); }
.panel-title { color: var(--text); font-size: 1.05rem; font-weight: 750; margin-bottom: 0.35rem; }
.panel-subtitle { color: #555650; font-size: 0.86rem; }
div[data-testid="stFileUploader"] { background: #FFFFFF; border: 1px dashed #C9C6BF; border-radius: 16px; padding: 0.85rem; }
.stTextArea textarea, .stTextInput input { background: #FFFFFF !important; color: var(--text) !important; border: 1px solid #DFDDD7 !important; border-radius: 12px !important; }
.stTextArea textarea:focus, .stTextInput input:focus { border-color: #9388E9 !important; box-shadow: 0 0 0 1px #9388E9 !important; }
.stButton > button, .stDownloadButton > button { background: #171717; color: #FFFFFF; border: 1px solid #171717; border-radius: 12px; min-height: 3.1rem; font-weight: 700; font-size: 0.96rem; width: 100%; transition: all 0.18s ease; }
.stButton > button:hover, .stDownloadButton > button:hover { background: #383838; border-color: #383838; color: #FFFFFF; box-shadow: 0 7px 18px rgba(0,0,0,0.12); }
.metric-card { background: #FFFFFF; border: 1px solid var(--border); border-radius: 17px; padding: 1.1rem; min-height: 125px; box-shadow: 0 8px 24px rgba(24,24,24,0.035); }
.metric-label { color: #555650; font-size: 0.83rem; }
.metric-value { color: var(--text); font-size: 2rem; font-weight: 800; margin-top: 0.45rem; }
.skill-tag { display: inline-block; background: #F4F3F0; border: 1px solid #E4E1DB; border-radius: 999px; padding: 0.38rem 0.7rem; margin: 0.2rem 0.25rem 0.2rem 0; color: #383833; font-size: 0.84rem; }
.recommendation { background: #FFFFFF; border: 1px solid var(--border); border-radius: 13px; padding: 0.9rem 1rem; margin-bottom: 0.65rem; color: #34342F; line-height: 1.6; box-shadow: 0 5px 16px rgba(24,24,24,0.025); }
div[data-testid="stProgressBar"] > div > div { background-color: var(--purple); }
div[data-testid="stTabs"] button { border-radius: 999px; }
hr { border-color: var(--border); margin: 1.5rem 0; }
[data-testid="stAlert"] { border-radius: 12px; }
[data-testid="stExpander"] { background: rgba(255,255,255,0.72); border: 1px solid var(--border); border-radius: 12px; }
@media (max-width: 700px) { .hero-title { letter-spacing: -1.5px; } .block-container { padding-left: 1rem; padding-right: 1rem; } }

/* Accessibility: improve contrast for secondary text while preserving the light workspace */
:root {
  --muted: #454545;
}
.eyebrow,
.feature-kicker,
.metric-top,
.metric-note,
.dashboard-subtitle,
.panel-subtitle,
.quick-card p,
.sidebar-foot span,
section[data-testid="stSidebar"] [data-testid="stRadio"] > label,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
[data-testid="stCaptionContainer"] p {
  color: #454545 !important;
}
.dashboard-title span,
.page-title span {
  color: #404040 !important;
}
.feature-copy,
.feature,
.metric-label,
.recommendation,
.skill-tag {
  color: #333333 !important;
}
.eyebrow {
  font-weight: 750 !important;
  letter-spacing: 1.8px !important;
}
.feature-kicker,
.metric-top,
.metric-note {
  font-weight: 650 !important;
}
.stApp p,
.stApp li,
.stApp label,
.stApp [data-testid="stMarkdownContainer"] {
  text-shadow: none;
}
.stTextArea textarea::placeholder,
.stTextInput input::placeholder {
  color: #666666 !important;
  opacity: 1 !important;
}

</style>

""",

          unsafe_allow_html=True,

)

# --------------------------------------------------

# HELPER FUNCTIONS

# --------------------------------------------------

def normalize(skill: str) -> str:

          """Normalize skill names for basic text comparison."""

          skill = skill.casefold().strip()

          skill = re.sub(r"[^a-z0-9+#. ]", " ", skill)

          return " ".join(skill.split())

def is_skill_match(required_skill: str, candidate_skills: list[str]) -> bool:

          """

          Compare a required skill with candidate skill labels using exact names

          and a small set of common aliases. This is not semantic matching.

          """

          required_name = normalize(required_skill)

          aliases = {

                    "python": ["python programming", "proficiency in python programming"],

                    "sql": [

                              "sql and relational databases",

                              "knowledge of sql and relational databases",

                              "mysql",

                              "sql queries",

                    ],

                    "git": [

                              "git and github",

                              "familiarity with git and github",

                              "version control",

                    ],

                    "github": ["git and github", "familiarity with git and github"],

                    "rest api": [

                              "rest apis",

                              "restful api",

                              "restful apis",

                              "understanding of rest apis and http methods",

                              "api development",

                    ],

                    "rest apis": [

                              "rest api",

                              "restful api",

                              "restful apis",

                              "understanding of rest apis and http methods",

                              "api development",

                    ],

                    "object oriented programming": [

                              "oop",

                              "understanding of object oriented programming oop",

                    ],

                    "oop": [

                              "object oriented programming",

                              "understanding of object oriented programming oop",

                    ],

                    "problem solving and debugging": [

                              "problem solving",

                              "debugging skills",

                    ],

          }

          accepted_names = {

                    required_name,

                    *(normalize(alias) for alias in aliases.get(required_name, [])),

          }

          for candidate in candidate_skills:

                    candidate_name = normalize(candidate)

                    candidate_aliases = {

                              candidate_name,

                              *(normalize(alias) for alias in aliases.get(candidate_name, [])),

                    }

                    if accepted_names.intersection(candidate_aliases):

                              return True

          return False



# Skills used for fast, local comparison between a resume and each job listing.
# This uses ordinary Python text matching, so it does not call the LLM for every job.
JOB_SKILL_TERMS = {
    "Python": ["python"],
    "Java": ["java"],
    "C": [r"\bc\b", "c programming"],
    "C++": ["c++"],
    "C#": ["c#"],
    "JavaScript": ["javascript", "java script"],
    "TypeScript": ["typescript"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "React": ["react", "react.js", "reactjs"],
    "Node.js": ["node.js", "nodejs"],
    "FastAPI": ["fastapi"],
    "Flask": ["flask"],
    "Django": ["django"],
    "REST APIs": ["rest api", "restful api", "rest apis", "restful apis"],
    "SQL": ["sql"],
    "MySQL": ["mysql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "MongoDB": ["mongodb", "mongo db"],
    "SQLite": ["sqlite"],
    "Database Management": ["database management", "dbms"],
    "Data Structures": ["data structures", "dsa"],
    "Algorithms": ["algorithms"],
    "Object-Oriented Programming": ["object oriented programming", "oop"],
    "Machine Learning": ["machine learning"],
    "Deep Learning": ["deep learning"],
    "Artificial Intelligence": ["artificial intelligence", "\\bai\\b"],
    "Scikit-learn": ["scikit-learn", "sklearn"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "NLP": ["natural language processing", "\\bnlp\\b"],
    "Computer Vision": ["computer vision"],
    "Data Analysis": ["data analysis", "data analytics"],
    "Statistics": ["statistics", "statistical analysis"],
    "Power BI": ["power bi"],
    "Tableau": ["tableau"],
    "Excel": ["microsoft excel", "\\bexcel\\b"],
    "Git": ["\\bgit\\b"],
    "GitHub": ["github"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes"],
    "Linux": ["linux"],
    "AWS": ["\\baws\\b", "amazon web services"],
    "Azure": ["microsoft azure", "\\bazure\\b"],
    "GCP": ["google cloud platform", "\\bgcp\\b"],
    "CI/CD": ["ci/cd", "continuous integration", "continuous delivery"],
    "Agile": ["agile"],
    "Testing": ["software testing", "unit testing", "pytest", "testing"],
    "Debugging": ["debugging"],
    "Problem Solving": ["problem solving"],
    "Communication": ["communication skills", "communication"],
}


def extract_skill_mentions(text_value):
    """Find known skill names in text using fast keyword/phrase matching."""
    text_value = str(text_value or "").casefold()
    found = []
    for skill_name, patterns in JOB_SKILL_TERMS.items():
        for pattern in patterns:
            if re.search(pattern, text_value, flags=re.IGNORECASE):
                found.append(skill_name)
                break
    return found


def split_job_skills(job_description):
    """Return skills explicitly mentioned in a job description."""
    return extract_skill_mentions(job_description)



def unique_strings(items: list[str]) -> list[str]:

          """Remove duplicate strings while preserving order."""

          output = []

          seen = set()

          for item in items:

                    key = normalize(item)

                    if key and key not in seen:

                              output.append(item.strip())

                              seen.add(key)

          return output

def render_skill_tags(skills: list[str], color: str) -> None:

          """Display skill names as HTML-escaped tags."""

          skills = unique_strings(skills)

          if not skills:

                    st.caption("No skills in this category.")

                    return

          tags = "".join(

                    f'<span class="skill-tag" style="border-color:{color}55">'

                    f'{html.escape(skill)}</span>'

                    for skill in skills

          )

          st.markdown(tags, unsafe_allow_html=True)

def classify_required_skills(required, matched, missing, unclear):

          """

          Make the required-skill categories mutually exclusive and calculate

          the score using the same required-skill list shown in the report.

          """

          required = unique_strings(required)

          matched = unique_strings(matched)

          missing = unique_strings(missing)

          unclear = unique_strings(unclear)

          matched_required = []

          missing_required = []

          unclear_required = []

          for skill in required:

                    if is_skill_match(skill, missing):

                              missing_required.append(skill)

                    elif is_skill_match(skill, unclear):

                              unclear_required.append(skill)

                    elif is_skill_match(skill, matched):

                              matched_required.append(skill)

                    else:

                              # If the model did not classify a required skill, do not count

                              # it as a match. Treat it as missing evidence for scoring.

                              missing_required.append(skill)

          total_required = len(required)

          match_score = (

                    round(len(matched_required) / total_required * 100)

                    if total_required

                    else 0

          )

          return (

                    required,

                    matched_required,

                    missing_required,

                    unclear_required,

                    total_required,

                    match_score,

          )

# --------------------------------------------------
# APP SHELL + SIDEBAR NAVIGATION
# --------------------------------------------------

if "talentlens_page" not in st.session_state:
    st.session_state["talentlens_page"] = "Dashboard"

def go_to_page(target_page):
    st.session_state["talentlens_page"] = target_page

with st.sidebar:
    st.markdown('<div class="brand">✦ TalentLens <span>AI</span></div>', unsafe_allow_html=True)
    st.caption("YOUR CAREER WORKSPACE")
    st.markdown("---")
    page = st.radio(
        "NAVIGATION",
        ["Dashboard", "Resume Analysis", "Job Discovery", "Career Roadmap"],
        key="talentlens_page",
        label_visibility="visible",
    )
    st.markdown("---")
    st.markdown("**Your resume**")
    resume_file = st.file_uploader(
        "Upload PDF or DOCX",
        type=["pdf", "docx"],
        key="talentlens_resume_upload",
        help="Your resume is used for analysis and skill comparisons.",
    )
    if resume_file is not None:
        st.success("Resume ready")
    else:
        st.caption("Upload a resume to unlock personalized insights.")
    st.markdown("---")
    st.markdown('<div class="sidebar-foot">✦ Your career workspace<br><span>Resume insights · Job search · Learning plan</span></div>', unsafe_allow_html=True)

header_left, header_right = st.columns([4, 1])
with header_left:
    st.markdown(f'<div class="eyebrow">TALENTLENS WORKSPACE / {html.escape(page.upper())}</div>', unsafe_allow_html=True)
with header_right:
    st.markdown('<div style="text-align:right;color:#555650;font-size:.82rem;padding-top:.2rem">✦ AI CAREER COPILOT</div>', unsafe_allow_html=True)

job_description = ""
analyze_clicked = False

if page == "Dashboard":
    st.markdown('<div class="dashboard-title">Good to see you.<br><span>Let’s move your career forward.</span></div>', unsafe_allow_html=True)
    st.markdown('<p class="dashboard-subtitle">Your resume, your skills, and your next opportunity — all in one place.</p>', unsafe_allow_html=True)
    analysis_snapshot = st.session_state.get("talentlens_analysis")
    job_snapshot = st.session_state.get("talentlens_job_result", {}) or {}
    jobs_snapshot = job_snapshot.get("jobs", []) if isinstance(job_snapshot, dict) else []
    score_snapshot = analysis_snapshot.get("match_score", 0) if analysis_snapshot else 0
    matched_snapshot = len(analysis_snapshot.get("matched_required_skills", [])) if analysis_snapshot else 0
    missing_snapshot = len(analysis_snapshot.get("missing_required_skills", [])) if analysis_snapshot else 0
    m1, m2, m3, m4 = st.columns(4, gap="medium")
    dashboard_metrics = [
        (m1, "RESUME STATUS", "Ready" if resume_file else "Not uploaded", "↗"),
        (m2, "SKILL MATCH", f"{score_snapshot}%" if analysis_snapshot else "—", "◌"),
        (m3, "SKILLS MATCHED", str(matched_snapshot) if analysis_snapshot else "—", "✓"),
        (m4, "JOBS DISCOVERED", str(len(jobs_snapshot)) if jobs_snapshot else "—", "⌕"),
    ]
    for col, label, value, symbol in dashboard_metrics:
        with col:
            st.markdown(f'<div class="metric-card dashboard-metric"><div class="metric-top"><span>{label}</span><b>{symbol}</b></div><div class="metric-value">{html.escape(value)}</div><div class="metric-note">{("Updated from your latest session" if analysis_snapshot or jobs_snapshot else "Start by uploading your resume")}</div></div>', unsafe_allow_html=True)
    st.markdown("<div class='section-heading'>Your workspace</div>", unsafe_allow_html=True)
    action1, action2 = st.columns([1.2, 1], gap="medium")
    with action1:
        st.markdown('''<div class="feature-card feature-card-dark"><div class="feature-kicker">01 / RESUME INTELLIGENCE</div><div class="feature-title">Know your strengths.<br>Close your skill gaps.</div><div class="feature-copy">Compare your resume with a job description and get a clear, evidence-based skill breakdown.</div></div>''', unsafe_allow_html=True)
        st.button("Open resume analysis  ↗", key="dashboard_open_analysis", use_container_width=True, on_click=go_to_page, args=("Resume Analysis",))
    with action2:
        st.markdown('''<div class="feature-card"><div class="feature-kicker">02 / OPPORTUNITY FINDER</div><div class="feature-title">Find roles that fit you.</div><div class="feature-copy">Explore public job listings and see which skills match your resume — and which ones to build next.</div></div>''', unsafe_allow_html=True)
        st.button("Explore job listings  ↗", key="dashboard_open_jobs", use_container_width=True, on_click=go_to_page, args=("Job Discovery",))
    st.markdown("<div class='section-heading'>Quick start</div>", unsafe_allow_html=True)
    q1, q2, q3 = st.columns(3, gap="medium")
    with q1:
        st.markdown('<div class="quick-card"><div class="quick-icon">↑</div><b>Upload your resume</b><p>Use the panel on the left to add your PDF or DOCX.</p></div>', unsafe_allow_html=True)
    with q2:
        st.markdown('<div class="quick-card"><div class="quick-icon">⌁</div><b>Analyze your fit</b><p>Paste a job description to identify matched and missing skills.</p></div>', unsafe_allow_html=True)
    with q3:
        st.markdown('<div class="quick-card"><div class="quick-icon">↗</div><b>Plan your next step</b><p>Discover roles and build a practical learning roadmap.</p></div>', unsafe_allow_html=True)

elif page == "Resume Analysis":
    st.markdown('<div class="page-title">Resume <span>analysis</span></div>', unsafe_allow_html=True)
    st.markdown('<p class="dashboard-subtitle">Compare your resume with a target job and get a clear view of your current fit.</p>', unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-title">Job description</div><div class="panel-subtitle">Paste the full job description for the most useful comparison.</div></div>', unsafe_allow_html=True)
    job_description = st.text_area(
        "Job description",
        placeholder="Paste the job description here...\n\nInclude required skills, preferred qualifications, and responsibilities.",
        height=220,
        label_visibility="collapsed",
        key="talentlens_jd_input",
    )
    analyze_clicked = st.button("✦  Analyze my resume", use_container_width=True, key="talentlens_analyze_button")
    if not resume_file:
        st.info("Upload your resume using the left sidebar to begin.")

elif page == "Job Discovery":
    st.markdown('<div class="page-title">Find your next <span>opportunity.</span></div>', unsafe_allow_html=True)
    st.markdown('<p class="dashboard-subtitle">Explore public job listings and compare each listing’s skills with your resume.</p>', unsafe_allow_html=True)

elif page == "Career Roadmap":
    st.markdown('<div class="page-title">Build your <span>next skill set.</span></div>', unsafe_allow_html=True)
    st.markdown('<p class="dashboard-subtitle">Discover adjacent roles and the skills you can learn to work toward them.</p>', unsafe_allow_html=True)

# ANALYSIS (persist in session_state so job-search clicks don't erase results)
# --------------------------------------------------

if "talentlens_analysis" not in st.session_state:
    st.session_state["talentlens_analysis"] = None

if analyze_clicked:
    # Clear previous analysis/job results when a new analysis is requested.
    st.session_state["talentlens_analysis"] = None
    st.session_state.pop("talentlens_job_result", None)
    st.session_state.pop("talentlens_job_query_input_last", None)

    if resume_file is None:
        st.error("Please upload a PDF or DOCX resume first.")
    elif not job_description.strip():
        st.error("Please enter a job description first.")
    else:
        try:
            with st.spinner("Analyzing your resume..."):
                parse_start = time.perf_counter()
                resume_text = extract_resume_text(
                    resume_file.name,
                    resume_file.getvalue(),
                )
                parse_seconds = time.perf_counter() - parse_start

                if not resume_text or not resume_text.strip():
                    raise ValueError(
                        "No readable text was found in the uploaded resume. "
                        "Please upload a text-based PDF or DOCX file."
                    )

                analysis_start = time.perf_counter()
                result = analyze_resume(resume_text, job_description)
                analysis_seconds = time.perf_counter() - analysis_start

            required = result["required_skills"]
            matched = result["matched_skills"]
            missing = result["missing_required_skills"]
            unclear = result["unclear_skills"]
            preferred = unique_strings(result["preferred_skills"])
            suggestions = unique_strings(result["suggestions"])

            (
                required,
                matched_required_skills,
                missing_required_skills,
                unclear_required_skills,
                total_required,
                match_score,
            ) = classify_required_skills(required, matched, missing, unclear)

            st.session_state["talentlens_analysis"] = {
                "required": required,
                "matched_required_skills": matched_required_skills,
                "missing_required_skills": missing_required_skills,
                "unclear_required_skills": unclear_required_skills,
                "total_required": total_required,
                "match_score": match_score,
                "preferred": preferred,
                "suggestions": suggestions,
                "parse_seconds": parse_seconds,
                "analysis_seconds": analysis_seconds,
            }
        except ValueError as error:
            st.error(f"Could not analyze the inputs: {error}")
        except RuntimeError as error:
            st.error("Resume analysis is temporarily unavailable. Please try again.")
            with st.expander("Details"):
                st.code(str(error))
        except Exception as error:
            st.error("The analysis failed. Please try again.")
            with st.expander("Details"):
                st.code(str(error))

# Render the saved analysis on every Streamlit rerun. Clicking the job-search
# button reruns the script, so results must be read back from session_state.
analysis = st.session_state.get("talentlens_analysis")
if analysis and page == "Resume Analysis":
    required = analysis["required"]
    matched_required_skills = analysis["matched_required_skills"]
    missing_required_skills = analysis["missing_required_skills"]
    unclear_required_skills = analysis["unclear_required_skills"]
    total_required = analysis["total_required"]
    match_score = analysis["match_score"]
    preferred = analysis["preferred"]
    suggestions = analysis["suggestions"]
    parse_seconds = analysis["parse_seconds"]
    analysis_seconds = analysis["analysis_seconds"]

    st.info(
        f"Resume parsing: {parse_seconds:.2f}s | AI analysis: {analysis_seconds:.2f}s"
    )
    st.markdown("---")
    st.markdown("## Your Analysis Results")
    st.caption("An evidence-based comparison of your resume with the job description.")

    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        (col1, "Required-skill match", f"{match_score}%", "#9475FF"),
        (col2, "Matched required", str(len(matched_required_skills)), "#45D6A1"),
        (col3, "Missing required", str(len(missing_required_skills)), "#FF718B"),
        (col4, "Unclear required", str(len(unclear_required_skills)), "#F6CB65"),
    ]
    for column, label, value, color in metrics:
        with column:
            st.markdown(
                f"""<div class="metric-card"><div class="metric-label">{html.escape(label)}</div><div class="metric-value" style="color:{color}">{html.escape(value)}</div></div>""",
                unsafe_allow_html=True,
            )

    st.progress(match_score / 100 if total_required else 0)
    st.caption(
        "Score = matched required skills divided by total required "
        f"skills ({len(matched_required_skills)} ÷ {total_required}). "
        "It measures skill coverage, not the probability of getting hired."
    )

    st.markdown("### Skill breakdown")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Matched", "Missing", "Unclear", "Preferred", "All requirements"]
    )
    with tab1:
        render_skill_tags(matched_required_skills, "#45D6A1")
    with tab2:
        render_skill_tags(missing_required_skills, "#FF718B")
    with tab3:
        render_skill_tags(unclear_required_skills, "#F6CB65")
    with tab4:
        render_skill_tags(preferred, "#9475FF")
    with tab5:
        st.markdown("**Required skills**")
        render_skill_tags(required, "#54D9F5")
        st.markdown("**Preferred skills**")
        render_skill_tags(preferred, "#9475FF")

    st.markdown("### Skills to learn for your next career role")
    if suggestions:
        for number, suggestion in enumerate(suggestions, start=1):
            st.markdown(
                f"""<div class="recommendation"><span style="color:#9475FF;font-weight:700">{number:02d}</span>&nbsp; {html.escape(suggestion)}</div>""",
                unsafe_allow_html=True,
            )
    else:
        st.info("No skill-to-role pathways were returned. Try analyzing again for tailored learning suggestions.")

    report = {
        "match_score_percent": match_score,
        "total_required_skills": total_required,
        "matched_required_skills": matched_required_skills,
        "missing_required_skills": missing_required_skills,
        "unclear_required_skills": unclear_required_skills,
        "preferred_skills": preferred,
        "suggestions": suggestions,
        "resume_parsing_seconds": round(parse_seconds, 2),
        "ai_analysis_seconds": round(analysis_seconds, 2),
    }
    st.download_button(
        "↓ Download Analysis Report (JSON)",
        data=json.dumps(report, indent=2, ensure_ascii=False),
        file_name="talentlens_analysis.json",
        mime="application/json",
        use_container_width=True,
    )

def build_resume_based_roadmap(resume_text: str) -> list[dict]:
    """Create fast, resume-grounded learning pathways without waiting on an LLM."""
    resume_skills = extract_skill_mentions(resume_text)
    if not resume_skills:
        return []

    profiles = [
        {"role": "Python Backend Developer", "core": ["Python", "SQL", "REST API", "FastAPI", "Git", "Docker"], "learn": ["FastAPI", "SQLAlchemy", "API testing", "Docker"], "project": "Build a FastAPI service with CRUD endpoints, MySQL persistence, validation, and tests.", "why": "Builds on Python and database knowledge while demonstrating backend API skills."},
        {"role": "Data Analyst", "core": ["Python", "SQL", "Pandas", "Data Visualization", "Power BI", "Statistics"], "learn": ["Pandas", "Statistics", "Power BI or Tableau", "SQL joins and window functions"], "project": "Analyze a public dataset, write SQL queries, and publish a dashboard with clear findings.", "why": "Connects programming and SQL foundations to practical data analysis and reporting."},
        {"role": "Machine Learning Engineer (Entry-Level Pathway)", "core": ["Python", "Machine Learning", "Scikit-learn", "Pandas", "Model Evaluation", "FastAPI"], "learn": ["Model evaluation", "Feature engineering", "Scikit-learn pipelines", "FastAPI deployment"], "project": "Train and evaluate a supervised-learning model, then expose predictions through a small API.", "why": "Strengthens the end-to-end workflow from data preparation to model serving."},
        {"role": "Data Engineer (Foundation Pathway)", "core": ["Python", "SQL", "MySQL", "ETL", "Docker", "Cloud Computing"], "learn": ["ETL pipelines", "Advanced SQL", "Data validation", "Docker"], "project": "Create a small ETL pipeline that ingests a public CSV, validates it, and loads it into a database.", "why": "Builds toward reliable data movement and transformation using programming and databases."},
    ]
    scored = []
    for profile in profiles:
        matched = [skill for skill in profile["core"] if is_skill_match(skill, resume_skills)]
        if matched:
            scored.append((len(matched), profile, matched))
    scored.sort(key=lambda item: item[0], reverse=True)

    pathways = []
    for _, profile, matched in scored[:3]:
        missing_to_learn = [skill for skill in profile["learn"] if not is_skill_match(skill, resume_skills)]
        evidence_sentence = ""
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", resume_text):
            if any(is_skill_match(skill, [sentence]) for skill in matched):
                evidence_sentence = sentence.strip()[:280]
                break
        pathways.append({
            "target_role": profile["role"],
            "current_evidence_quote": evidence_sentence,
            "current_foundation": "Resume skills detected for this pathway: " + ", ".join(matched) + ".",
            "skills_to_learn": missing_to_learn[:4],
            "next_project": profile["project"],
            "why_it_helps": profile["why"],
        })
    return pathways


# --------------------------------------------------
# JOB DISCOVERY — listings and resume-to-job skill comparison only
# CAREER ROADMAP — future roles and learning pathways only
# --------------------------------------------------

if "talentlens_resume_fingerprint" not in st.session_state:
    st.session_state["talentlens_resume_fingerprint"] = None
if "talentlens_resume_text" not in st.session_state:
    st.session_state["talentlens_resume_text"] = ""
if "talentlens_job_keywords" not in st.session_state:
    st.session_state["talentlens_job_keywords"] = []
if "talentlens_keywords_fingerprint" not in st.session_state:
    st.session_state["talentlens_keywords_fingerprint"] = None
if "talentlens_resume_skills" not in st.session_state:
    st.session_state["talentlens_resume_skills"] = []
if "talentlens_job_query_input" not in st.session_state:
    st.session_state["talentlens_job_query_input"] = ""
if "talentlens_skill_pathways" not in st.session_state:
    st.session_state["talentlens_skill_pathways"] = []

if resume_file is not None:
    current_fingerprint = hashlib.sha256(resume_file.getvalue()).hexdigest()
    if st.session_state["talentlens_resume_fingerprint"] != current_fingerprint:
        st.session_state["talentlens_resume_fingerprint"] = current_fingerprint
        st.session_state["talentlens_resume_text"] = ""
        st.session_state["talentlens_job_keywords"] = []
        st.session_state["talentlens_resume_skills"] = []
        st.session_state["talentlens_job_query_input"] = ""
        st.session_state["talentlens_skill_pathways"] = []
        # Clear all resume-dependent state, including Streamlit's text-input value.
        st.session_state["talentlens_job_query_input"] = ""
        st.session_state["talentlens_keywords_fingerprint"] = None
        st.session_state.pop("talentlens_job_result", None)
        st.session_state.pop("talentlens_job_query_input_last", None)


def ensure_resume_text():
    """Parse the uploaded resume once per file and reuse it across pages."""
    if resume_file is None:
        raise ValueError("Upload your resume from the sidebar to continue.")
    if not st.session_state.get("talentlens_resume_text", "").strip():
        parsed = extract_resume_text(resume_file.name, resume_file.getvalue())
        if not parsed or not parsed.strip():
            raise ValueError("No readable text was found. Upload a text-based PDF or DOCX resume.")
        st.session_state["talentlens_resume_text"] = parsed
    return st.session_state["talentlens_resume_text"]


def rank_resume_roles(resume_text: str, suggested_roles: list[str]) -> list[str]:
    """Rank job-search roles from strong, role-specific resume evidence."""
    text = re.sub(r"\\s+", " ", (resume_text or "").casefold())
    has = lambda *terms: any(term in text for term in terms)
    project = has("project", "built", "developed", "implemented", "created",
                  "portfolio", "application", "dashboard", "website")

    evidence_roles = []

    # Frontend roles come first when the resume shows the web stack and interface work.
    frontend_stack = (
        has("html", "html5")
        and has("css", "css3", "flexbox", "css grid")
        and has("javascript", "javascript es6", "react", "typescript")
    )
    frontend_work = has(
        "responsive", "portfolio", "frontend", "front-end", "dom manipulation",
        "form validation", "mobile-first", "website", "interface", "weather dashboard"
    )
    if frontend_stack and frontend_work and project:
        evidence_roles.extend(["Frontend Developer Intern", "Web Developer Intern"])

    # Python Developer requires evidence that Python itself was used to build software.
    # A basic Python skill, JavaScript REST API project, or generic project is insufficient.
    python_build_evidence = has(
        "fastapi", "flask", "django", "python application", "python script",
        "python project", "built with python", "developed using python",
        "python backend", "pytest", "python-based"
    )
    beginner_python = has(
        "basic python", "basic knowledge of python", "beginner python",
        "introductory python", "python (basic)", "python - basic"
    )
    if has("python") and python_build_evidence and not beginner_python:
        evidence_roles.append("Python Developer Intern")

    # Backend roles require a server-side framework or explicit backend project evidence.
    backend_work = has(
        "fastapi", "flask", "django", "node.js", "express.js",
        "backend project", "back-end project", "server-side implementation",
        "built a backend", "developed a backend"
    )
    if backend_work and project:
        evidence_roles.append("Backend Developer Intern")

    if has("machine learning", "scikit-learn", "sklearn", "tensorflow", "pytorch") and has(
        "classification", "regression", "prediction", "trained model", "dataset", "model evaluation"
    ) and project:
        evidence_roles.append("Machine Learning Intern")

    if has("data analysis", "data analyst", "exploratory data analysis", "eda",
           "data cleaning", "pandas", "numpy", "data visualization") and has(
        "sql", "mysql", "excel", "power bi", "tableau", "matplotlib", "seaborn", "dashboard"
    ) and project:
        evidence_roles.append("Data Analyst Intern")

    # Only keep AI suggestions when they do not contradict stronger resume evidence.
    filtered_suggestions = []
    for role in suggested_roles or []:
        title = str(role).strip()
        lower = title.casefold()
        if any(term in lower for term in ("python developer", "python engineer", "python programmer")):
            if "Python Developer Intern" not in evidence_roles:
                continue
        if any(term in lower for term in ("backend developer", "back-end developer", "backend engineer")):
            if "Backend Developer Intern" not in evidence_roles:
                continue
        if any(term in lower for term in ("frontend developer", "front-end developer", "web developer")):
            if not frontend_stack or not frontend_work or not project:
                continue
        filtered_suggestions.append(title)

    ordered = []
    seen = set()
    for role in evidence_roles + filtered_suggestions:
        key = re.sub(r"[^a-z0-9]+", " ", str(role).casefold()).strip()
        if key and key not in seen:
            seen.add(key)
            ordered.append(str(role).strip())
        if len(ordered) >= 5:
            break
    return ordered

def ensure_resume_keywords():
    """Extract job-search keywords only for the currently uploaded resume."""
    if resume_file is None:
        raise ValueError("Upload your resume from the sidebar to continue.")

    current_fingerprint = hashlib.sha256(resume_file.getvalue()).hexdigest()
    cached = st.session_state.get("talentlens_job_keywords", [])
    cached_fingerprint = st.session_state.get("talentlens_keywords_fingerprint")

    # Never reuse keywords generated from a different uploaded file.
    if cached and cached_fingerprint == current_fingerprint:
        return cached

    st.session_state["talentlens_job_keywords"] = []
    st.session_state["talentlens_resume_text"] = ""
    st.session_state["talentlens_resume_skills"] = []
    st.session_state["talentlens_job_query_input"] = ""
    st.session_state.pop("talentlens_job_result", None)
    st.session_state.pop("talentlens_job_query_input_last", None)

    resume_text = ensure_resume_text()
    generated = generate_job_keywords(resume_text)
    if isinstance(generated, str):
        generated = [item.strip() for item in re.split(r"[,\n;]+", generated) if item.strip()]
    keywords = unique_strings([str(item).strip() for item in (generated or []) if str(item).strip()])
    # The first search query should reflect the current resume's evidence, not
    # blindly trust a generic AI title or a previous resume's cached selection.
    keywords = rank_resume_roles(resume_text, keywords)
    if not keywords:
        raise ValueError("No job-search keywords could be extracted from this resume. Check that the resume text is readable and try uploading it again.")
    st.session_state["talentlens_job_keywords"] = keywords
    st.session_state["talentlens_keywords_fingerprint"] = current_fingerprint
    st.session_state["talentlens_job_query_input"] = keywords[0]
    st.session_state["talentlens_resume_skills"] = extract_skill_mentions(resume_text)
    return keywords


# Prepare resume-derived data once after upload, then reuse it on both pages.
# This avoids blank job-search inputs and prevents repeated model calls per listing.
if resume_file is not None:
    try:
        ensure_resume_text()
        if not st.session_state.get("talentlens_job_keywords"):
            ensure_resume_keywords()
    except Exception as resume_setup_error:
        st.session_state["talentlens_resume_setup_error"] = str(resume_setup_error)
    else:
        st.session_state.pop("talentlens_resume_setup_error", None)
else:
    st.session_state.pop("talentlens_resume_setup_error", None)


if page == "Job Discovery":
    st.markdown("## Job listings matched to your resume")
    st.caption("Search listings using keywords extracted from your uploaded resume. You can edit the search if needed.")

    keywords = st.session_state.get("talentlens_job_keywords", [])
    if resume_file is None:
        st.info("Upload a resume from the sidebar to prepare your job search automatically.")
    elif st.session_state.get("talentlens_resume_setup_error"):
        st.error("Resume keywords could not be prepared. Please check that your PDF or DOCX contains readable text.")
        with st.expander("Details"):
            st.code(st.session_state["talentlens_resume_setup_error"])

    job_query = st.text_input(
        "Search keywords extracted from your resume",
        key="talentlens_job_query_input",
        placeholder="Keywords will appear here after resume upload",
        help="Automatically populated from your resume. Edit only if you want to search for a different role.",
        disabled=not bool(keywords),
    )
    if st.button("Search job listings", key="talentlens_find_jobs", use_container_width=True, disabled=not bool(keywords)):
        try:
            with st.spinner("Searching job listings…"):
                resume_text = ensure_resume_text()
                effective_query = st.session_state.get("talentlens_job_query_input", "").strip()
                if not effective_query:
                    effective_query = keywords[0]
                    st.session_state["talentlens_job_query_input"] = effective_query
                st.session_state["talentlens_resume_skills"] = st.session_state.get("talentlens_resume_skills") or extract_skill_mentions(resume_text)
                result = search_jobs_fast(effective_query, max_results=12)
                st.session_state["talentlens_job_result"] = result
                st.session_state["talentlens_job_query_input_last"] = effective_query
        except Exception as job_error:
            st.session_state["talentlens_job_result"] = {"jobs": [], "search_links": [], "errors": [str(job_error)]}
            st.session_state["talentlens_job_query_input_last"] = st.session_state.get("talentlens_job_query_input", "")
            st.error("Job search could not be completed. Please try again.")
            with st.expander("Details"):
                st.code(str(job_error))

    job_result = st.session_state.get("talentlens_job_result")
    if job_result:
        st.caption(f"Results for: {st.session_state.get('talentlens_job_query_input_last', '')}")
        jobs = job_result.get("jobs", [])
        if jobs:
            st.success(f"Found {len(jobs)} job listing(s). Review each listing for current availability and eligibility.")
            resume_text_for_match = st.session_state.get("talentlens_resume_text", "")
            resume_skills_for_match = st.session_state.get("talentlens_resume_skills", [])
            if resume_text_for_match.strip() and not resume_skills_for_match:
                resume_skills_for_match = extract_skill_mentions(resume_text_for_match)
                st.session_state["talentlens_resume_skills"] = resume_skills_for_match

            for job in jobs:
                title = str(job.get("title", "Job title not provided"))
                company = str(job.get("company", "Company not specified"))
                location = str(job.get("location", "Location not specified"))
                source = str(job.get("source", "Job board"))
                url = str(job.get("url", ""))
                remote_note = " · Remote" if job.get("remote") else ""
                with st.container(border=True):
                    if url.startswith(("https://", "http://")):
                        st.markdown(f"### [{html.escape(title)}]({url})")
                        st.markdown(f"[View job listing / apply ↗]({url})")
                    else:
                        st.markdown(f"### {html.escape(title)}")
                    st.write(f"{company} · {location}{remote_note}")
                    st.caption(f"Source: {source}")
                    description = re.sub(r"<[^>]+>", " ", str(job.get("description", "")))
                    description = re.sub(r"\s+", " ", description).strip()
                    if description:
                        st.write(description[:500] + ("…" if len(description) > 500 else ""))

                    job_skills = split_job_skills(description)
                    if not resume_text_for_match.strip():
                        st.info("Upload a resume from the sidebar to compare skills for this listing.")
                    elif not description or not job_skills:
                        st.caption("A skills comparison is unavailable because this listing has limited skill information.")
                    else:
                        matched_job_skills = [skill for skill in job_skills if is_skill_match(skill, resume_skills_for_match)]
                        missing_job_skills = [skill for skill in job_skills if not is_skill_match(skill, resume_skills_for_match)]
                        left, right = st.columns(2)
                        with left:
                            st.markdown("**Skills found in your resume**")
                            if matched_job_skills:
                                render_skill_tags(matched_job_skills, "#16845D")
                            else:
                                st.caption("No matching skills identified.")
                        with right:
                            st.markdown("**Skills not found in your resume**")
                            if missing_job_skills:
                                render_skill_tags(missing_job_skills, "#C34C5B")
                            else:
                                st.caption("All detected listing skills were found in your resume.")
        else:
            st.warning("No matching listings were found from the available public sources. Try another job title.")
        if job_result.get("errors"):
            with st.expander("Job source status"):
                for source_error in job_result["errors"]:
                    st.caption(str(source_error))
        links = job_result.get("search_links", [])
        if links:
            st.markdown("**Explore more listings**")
            for link in links:
                link_title = html.escape(str(link.get("title", "Search jobs")))
                link_url = str(link.get("url", "#"))
                st.markdown(f"- [{link_title}]({link_url})")

elif page == "Career Roadmap":
    st.markdown("## Skills and roles to work toward")
    st.caption("Resume-based role pathways, skill gaps, and practice projects.")

    if st.button("Generate career roadmap", key="talentlens_generate_roadmap", use_container_width=True, disabled=resume_file is None):
        try:
            with st.spinner("Building your roadmap from the skills in your resume…"):
                resume_text = ensure_resume_text()
                pathways = build_resume_based_roadmap(resume_text)
                st.session_state["talentlens_skill_pathways"] = pathways
                st.session_state["talentlens_roadmap_generated"] = True
        except Exception as roadmap_error:
            st.session_state["talentlens_skill_pathways"] = []
            st.session_state["talentlens_roadmap_generated"] = True
            st.error("The career roadmap could not be generated.")
            with st.expander("Technical details"):
                st.exception(roadmap_error)

    pathways = st.session_state.get("talentlens_skill_pathways", [])
    if pathways:
        st.success(f"Generated {len(pathways)} career pathway(s) from your resume skills.")
        for index, pathway in enumerate(pathways, start=1):
            with st.container(border=True):
                st.markdown(f"### {index}. {html.escape(str(pathway.get('target_role', 'Suggested role')))}")
                evidence = str(pathway.get("current_evidence_quote", "")).strip()
                foundation = str(pathway.get("current_foundation", "")).strip()
                if evidence:
                    st.markdown("**Evidence from your resume**")
                    st.write(f"“{evidence}”")
                if foundation:
                    st.write(foundation)
                skills_to_learn = pathway.get("skills_to_learn", [])
                st.markdown("**Skills to learn next**")
                if skills_to_learn:
                    render_skill_tags([str(skill) for skill in skills_to_learn], "#6557D9")
                else:
                    st.write("Your detected skills cover this pathway's listed foundation. Practise them in a project and review real job requirements next.")
                st.markdown("**Practice project**")
                st.write(str(pathway.get("next_project", "")))
                st.markdown("**Why this pathway fits**")
                st.write(str(pathway.get("why_it_helps", "")))
        st.caption("These are learning directions inferred from skills found in your resume, not a guarantee of job eligibility.")
    elif resume_file is None:
        st.info("Upload your resume from the sidebar to generate a personalized career roadmap.")
    elif st.session_state.get("talentlens_roadmap_generated"):
        st.warning("I couldn't identify enough known skills in this resume to recommend a pathway. Check that the uploaded PDF/DOCX contains selectable text and includes your skills or projects.")
    else:
        st.info("Select Generate career roadmap to view recommended roles, skills, and practice projects.")


# FOOTER

# --------------------------------------------------

st.divider()

st.caption("TalentLens AI · Resume insights, job discovery, and career planning")
