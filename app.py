import html

import json

import re

import time

import streamlit as st

from resume_parser import extract_resume_text

from llm_analyzer import analyze_resume
from job_discovery_agent import search_jobs_fast

# --------------------------------------------------

# PAGE CONFIGURATION

# --------------------------------------------------

st.set_page_config(

          page_title="TalentLens AI",

          page_icon="✦",

          layout="wide",

          initial_sidebar_state="collapsed",

)

# --------------------------------------------------

# CUSTOM STYLING

# --------------------------------------------------

st.markdown(

          """

<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {

--bg: #080B14;

--panel: #101626;

--border: #252E45;

--text: #F4F5FC;

--muted: #9AA6C0;

--purple: #9475FF;

--green: #45D6A1;

--red: #FF718B;

--yellow: #F6CB65;

}

.stApp {

background:

radial-gradient(ellipse at 15% 0%, #21164A 0%, transparent 36%),

var(--bg);

color: var(--text);

font-family: 'Inter', sans-serif;

}

.block-container {

max-width: 1240px;

padding-top: 1.5rem;

padding-bottom: 3rem;

}

header[data-testid="stHeader"] {

background: transparent;

}

#MainMenu, footer {

visibility: hidden;

}

.brand {

font-size: 1.45rem;

font-weight: 800;

letter-spacing: -0.8px;

color: var(--text);

}

.brand span, .accent {

color: var(--purple);

}

.eyebrow {

color: var(--purple);

font-size: 0.75rem;

font-weight: 700;

letter-spacing: 2.5px;

text-transform: uppercase;

}

.hero-title {

font-size: clamp(2.6rem, 5vw, 4.4rem);

font-weight: 800;

letter-spacing: -3px;

line-height: 1.05;

color: var(--text);

margin: 1rem 0;

}

.hero-title span {

color: var(--purple);

}

.feature {

color: #D9DDF0;

font-size: 0.9rem;

padding: 0.7rem 0;

}

.panel {

background: linear-gradient(145deg, #121A2C, #0D1322);

border: 1px solid var(--border);

border-radius: 14px;

padding: 1.1rem 1.2rem;

margin-bottom: 0.5rem;

}

.panel-title {

color: var(--text);

font-size: 1.05rem;

font-weight: 700;

margin-bottom: 0.35rem;

}

.panel-subtitle {

color: var(--muted);

font-size: 0.86rem;

}

div[data-testid="stFileUploader"] {

background: #0C1221;

border: 1px dashed #4D477D;

border-radius: 12px;

padding: 0.8rem;

}

.stTextArea textarea {

background: #0C1221 !important;

color: var(--text) !important;

border: 1px solid var(--border) !important;

border-radius: 10px !important;

}

.stButton > button,

.stDownloadButton > button {

background: linear-gradient(100deg, #5840F5, #9560F8);

color: white;

border: none;

border-radius: 10px;

min-height: 3.3rem;

font-weight: 700;

font-size: 1rem;

width: 100%;

transition: 0.2s ease;

}

.stButton > button:hover,

.stDownloadButton > button:hover {

border: 1px solid #B9A6FF;

box-shadow: 0 0 24px #7654F544;

color: white;

}

.metric-card {

background: linear-gradient(145deg, #121A2C, #0D1322);

border: 1px solid var(--border);

border-radius: 14px;

padding: 1.1rem;

min-height: 125px;

}

.metric-label {

color: var(--muted);

font-size: 0.83rem;

}

.metric-value {

color: var(--text);

font-size: 2rem;

font-weight: 800;

margin-top: 0.45rem;

}

.skill-tag {

display: inline-block;

background: #171E31;

border: 1px solid #303B56;

border-radius: 7px;

padding: 0.4rem 0.65rem;

margin: 0.2rem 0.25rem 0.2rem 0;

color: #E3E7F6;

font-size: 0.85rem;

}

.recommendation {

background: #12152A;

border: 1px solid #39305D;

border-radius: 10px;

padding: 0.85rem 1rem;

margin-bottom: 0.6rem;

color: #E3E7F6;

line-height: 1.6;

}

div[data-testid="stProgressBar"] > div > div {

background-color: var(--purple);

}

hr {

border-color: var(--border);

margin: 1.5rem 0;

}

@media (max-width: 700px) {

.hero-title {

letter-spacing: -1.5px;

}

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

# NAVIGATION

# --------------------------------------------------

nav1, nav2, nav3 = st.columns([3, 1, 1])

with nav1:

          st.markdown(

                    '<div class="brand">✦ TalentLens <span>AI</span></div>',

                    unsafe_allow_html=True,

          )

with nav2:

          st.caption("AI RESUME ANALYZER")

with nav3:

          st.caption("POWERED BY OLLAMA")

st.divider()

# --------------------------------------------------

# HERO

# --------------------------------------------------

st.markdown(

          '<div class="eyebrow">YOUR NEXT OPPORTUNITY STARTS HERE</div>',

          unsafe_allow_html=True,

)

st.markdown(

          '<div class="hero-title">Turn Your Resume<br>'

          'Into <span>Opportunities.</span></div>',

          unsafe_allow_html=True,

)

st.markdown(

          "Understand your fit for a role, uncover skill gaps, "

          "and get actionable recommendations powered by local AI."

)

st.markdown(

          """

<div class="feature">

✦ &nbsp; Evidence-based skill matching

&nbsp;&nbsp;&nbsp; ✦ &nbsp; Skill-gap identification

&nbsp;&nbsp;&nbsp; ✦ &nbsp; Personalized recommendations

</div>

""",

          unsafe_allow_html=True,

)

st.markdown("<br>", unsafe_allow_html=True)

# --------------------------------------------------

# INPUT SECTION

# --------------------------------------------------

left, right = st.columns(2, gap="large")

with left:

          st.markdown(

                    """

<div class="panel">

<div class="panel-title">01 &nbsp; Upload your resume</div>

<div class="panel-subtitle">

PDF or DOCX · Upload your latest resume

</div>

</div>

""",

                    unsafe_allow_html=True,

          )

          resume_file = st.file_uploader(

                    "Choose your resume",

                    type=["pdf", "docx"],

                    help="Upload a text-based PDF or DOCX resume.",

          )

with right:

          st.markdown(

                    """

<div class="panel">

<div class="panel-title">02 &nbsp; Job description</div>

<div class="panel-subtitle">

Add the role requirements and responsibilities

</div>

</div>

""",

                    unsafe_allow_html=True,

          )

          job_description = st.text_area(

                    "Job description",

                    placeholder=(

                              "Paste the job description here...\n\n"

                              "Include required skills, preferred qualifications, "

                              "and responsibilities."

                    ),

                    height=190,

                    label_visibility="collapsed",

          )

st.markdown("<br>", unsafe_allow_html=True)

analyze_clicked = st.button(
    "✦     Analyze My Resume",
    use_container_width=True,
)

# --------------------------------------------------
# ANALYSIS (persist in session_state so job-search clicks don't erase results)
# --------------------------------------------------

if "talentlens_analysis" not in st.session_state:
    st.session_state["talentlens_analysis"] = None

if analyze_clicked:
    # Clear previous analysis/job results when a new analysis is requested.
    st.session_state["talentlens_analysis"] = None
    st.session_state.pop("talentlens_job_result", None)
    st.session_state.pop("talentlens_job_query_last", None)

    if resume_file is None:
        st.error("Please upload a PDF or DOCX resume first.")
    elif not job_description.strip():
        st.error("Please enter a job description first.")
    else:
        try:
            with st.spinner("Analyzing your resume with local AI..."):
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
            st.error(str(error))
            st.info(
                "Check that Ollama is running and the configured model "
                "is installed. For example: ollama list"
            )
        except Exception as error:
            st.error("The analysis failed. Please try again.")
            with st.expander("Technical details"):
                st.code(str(error))

# Render the saved analysis on every Streamlit rerun. Clicking the job-search
# button reruns the script, so results must be read back from session_state.
analysis = st.session_state.get("talentlens_analysis")
if analysis:
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

    st.markdown("### Personalized recommendations")
    if suggestions:
        for number, suggestion in enumerate(suggestions, start=1):
            st.markdown(
                f"""<div class="recommendation"><span style="color:#9475FF;font-weight:700">{number:02d}</span>&nbsp; {html.escape(suggestion)}</div>""",
                unsafe_allow_html=True,
            )
    else:
        st.info("No recommendations were returned.")

    st.markdown("### Find matching jobs & internships")
    st.caption(
        "Search public job boards separately from resume analysis. "
        "Listings and eligibility depend on each source."
    )
    job_query = st.text_input(
        "Job search keywords",
        value="python developer intern",
        key="talentlens_job_query",
        placeholder="e.g. Python intern, data analyst fresher",
    )
    if st.button(
        "🔎 Find Matching Jobs",
        key="talentlens_find_jobs",
        use_container_width=True,
    ):
        if not job_query.strip():
            st.warning("Enter a job title or skill to search.")
        else:
            with st.spinner("Searching public job boards…"):
                try:
                    job_result = search_jobs_fast(job_query.strip(), max_results=12)
                    st.session_state["talentlens_job_result"] = job_result
                    st.session_state["talentlens_job_query_last"] = job_query.strip()
                except Exception as job_error:
                    st.session_state["talentlens_job_result"] = {
                        "jobs": [],
                        "search_links": [],
                        "errors": [str(job_error)],
                    }
                    st.session_state["talentlens_job_query_last"] = job_query.strip()

    job_result = st.session_state.get("talentlens_job_result")
    if job_result:
        st.caption(
            f"Results for: {st.session_state.get('talentlens_job_query_last', job_query)}"
        )
        jobs = job_result.get("jobs", [])
        if jobs:
            st.success(
                f"Found {len(jobs)} matching listing(s). Check each listing for current availability and eligibility."
            )
            for job in jobs:
                title = str(job.get("title", "Job title not provided"))
                company = str(job.get("company", "Company not specified"))
                location = str(job.get("location", "Location not specified"))
                source = str(job.get("source", "Job board"))
                url = str(job.get("url", ""))
                remote_note = " · Remote" if job.get("remote") else ""
                with st.container(border=True):
                    if url.startswith(("https://", "http://")):
                        st.markdown(f"**[{html.escape(title)}]({url})**")
                        st.markdown(f"[Open application / listing ↗]({url})")
                    else:
                        st.markdown(f"**{html.escape(title)}**")
                    st.write(f"{company} · {location}{remote_note}")
                    st.caption(f"Source: {source}")
                    description = re.sub(r"<[^>]+>", " ", str(job.get("description", "")))
                    description = re.sub(r"\s+", " ", description).strip()
                    if description:
                        st.write(description[:320] + ("…" if len(description) > 320 else ""))
        else:
            st.warning(
                "No matching entry-level listings were found from the connected public sources right now."
            )
        if job_result.get("errors"):
            with st.expander("Job source status"):
                for source_error in job_result["errors"]:
                    st.caption(str(source_error))
        links = job_result.get("search_links", [])
        if links:
            st.markdown("**More job-search links**")
            for link in links:
                link_title = html.escape(str(link.get("title", "Search jobs")))
                link_url = str(link.get("url", "#"))
                st.markdown(f"- [{link_title}]({link_url})")

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

# --------------------------------------------------

# FOOTER

# --------------------------------------------------

st.divider()

st.caption("TalentLens AI · Built with Streamlit and Ollama · Local AI analysis")
