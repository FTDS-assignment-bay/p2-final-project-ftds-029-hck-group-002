# joblist.py
import streamlit as st
from PIL import Image

# ===== Custom CSS =====
st.markdown("""
<style>
/* Background gradient */
.stApp {
    background: linear-gradient(135deg, #4f00bc, #29abe2);
    color: white;
}

/* Job list buttons */
button[kind="secondary"] {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.3);
    color: white;
    border-radius: 6px;
}
button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.2);
}

/* Apply button */
button[kind="primary"] {
    background: linear-gradient(to right, #00c6ff, #0072ff);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: bold;
}
button[kind="primary"]:hover {
    background: linear-gradient(to right, #0072ff, #00c6ff);
}

/* Headings */
h1, h2, h3, h4 {
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ===== Sample Data =====
jobs = [
    {
        "title": "Data Engineer",
        "company": "EY (Ernst & Young LLP)",
        "location": "Jakarta, Indonesia",
        "posted": "August 12th 2025",
        "type": "Full-time",
        "description": """
**About EY**  
EY is a global leader operating in 150+ countries, delivering consulting services and helping clients transform capabilities. We aim to build a better working world through trust, innovation, and long-term value creation.

**Requirements**  
- Bachelor’s degree in Information Systems, Computer Science, Informatics, or related field.  
- 1–2 years (Associate) or 3–5 years (Senior) in data engineering.  

**Responsibilities**  
- Collect, process, and analyze large datasets.  
- Develop and maintain dashboards/reports using Microsoft Power BI.  
- Collaborate with teams to identify data needs.  
- Conduct data quality assessments and ensure integrity.  

**Technical Skills**  
- Data collection, processing & analysis  
- Identifying trends & patterns  
- Data visualization/dashboard development  
- Data quality & integrity assurance  

**Tools**  
- Power BI  
- SQL-based databases  

**Soft Skills**  
- Teamwork, adaptability, strong communication, consulting experience
        """,
    },
    {
        "title": "Data Scientist",
        "company": "PT Astra International Tbk",
        "location": "Jakarta, Indonesia",
        "posted": "June 12th 2025",
        "type": "Full-time",
        "description": """
**About the Role**  
Responsible for building systems and tools to collect, clean, and distribute data from various sources, performing statistical analysis, and preparing visualizations to understand trends and patterns.

**Requirements**  
- Bachelor’s degree in Statistics, Mathematics, Computer Science, or Information Systems.  
- Preferably 1+ years’ experience; open to fresh graduates.  
- Strong analytical and conceptual thinking.  
- High motivation, integrity, and leadership potential.  

**Responsibilities**  
- Develop predictive models and perform statistical analyses.  
- Prepare reports and dashboards for business insights.  
- Collaborate with teams for data-driven decision-making.  

**Soft Skills**  
- Discipline, quick learner, positive attitude, leadership skills
        """,
    }
]

# ===== Job Finder App Function =====
def job_finder_app(jobs):
    col1, col2 = st.columns([1, 2])

    # Left Panel: Job list
    with col1:
        st.subheader("📋 Job Vacancies")
        for i, job in enumerate(jobs):
            if st.button(f"{job['title']} – {job['company']}", key=f"job_{i}", type="secondary", use_container_width=True):
                st.session_state["selected_job"] = i

    # Default selection
    if "selected_job" not in st.session_state:
        st.session_state["selected_job"] = 0

    # Right Panel: Job details
    with col2:
        job = jobs[st.session_state["selected_job"]]
        st.subheader(job["title"])
        st.write(f"**Company:** {job['company']}")
        st.write(f"**Location:** {job['location']}")
        st.write(f"**Posted:** {job['posted']}")
        st.write(f"**Type:** {job['type']}")
        st.markdown(job["description"])
        st.markdown("---")

        # Apply button
        if st.button("Apply ✅", type="primary"):
            if job["title"] == "Data Scientist":
                st.switch_page("pages/scandidai_ds.py")
            elif job["title"] == "Data Engineer":
                st.switch_page("pages/scandidai_de.py")

# ===== Optional: run app if main =====
if __name__ == "__main__":
    job_finder_app(jobs)
