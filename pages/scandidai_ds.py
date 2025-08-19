# scandidai_ds.py
import streamlit as st
from pdfminer.high_level import extract_text
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq
import re
from dotenv import load_dotenv
import sys
import os
import pandas as pd
from PIL import Image
from datetime import datetime

# ===== Set page config =====
st.set_page_config(page_title="Data Scientist Screening", layout="wide")

# ===== Custom CSS Styling =====
st.markdown("""
<style>
/* Background gradient */
.stApp {
    background: linear-gradient(135deg, #4f00bc, #29abe2);
    color: white;
}

/* Form Card */
.form-card {
    background-color: rgba(0,0,0,0.6);
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
}

/* Text area styling */
textarea {
    background-color: rgba(255,255,255,0.1);
    color: white;
    border-radius: 8px;
}

/* Score cards */
.score-card {
    background: rgba(255,255,255,0.1);
    padding: 15px;
    border-radius: 10px;
    text-align: center;
}

/* AI Report Box */
.report-box {
    background-color: rgba(0,0,0,0.8);
    color: #ffffff;
    padding: 15px;
    border-radius: 10px;
    max-height: 400px;
    overflow-y: auto;
    font-family: monospace;
}

/* Download button */
.stButton>button {
    background: linear-gradient(to right, #00c6ff, #0072ff);
    color: white;
    font-weight: bold;
    border-radius: 10px;
}
.stButton>button:hover {
    background: linear-gradient(to right, #0072ff, #00c6ff);
}
</style>
""", unsafe_allow_html=True)

# ===== Cek login =====
if "logged_in" not in st.session_state or not st.session_state.logged_in or "username" not in st.session_state:
    st.warning("⚠️ Silakan login terlebih dahulu.")
    st.stop()

username = st.session_state.username
st.title(f"👋 Hi, {username}")

# ===== Import jobs (tanpa set_page_config) =====
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from pages.joblist import jobs

data_scientist_job = next((j for j in jobs if j["title"].lower() == "data scientist"), None)
if not data_scientist_job:
    st.error("Data scientist job not found in joblist.py")
    st.stop()

job_desc = data_scientist_job["description"]

# ===== Load environment variables =====
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# ===== Session State =====
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "open_question" not in st.session_state:
    st.session_state.open_question = ""

st.title("scandidAI – Data Scientist Role Screening")

# ===== Functions =====
def extract_pdf_text(uploaded_file):
    try:
        return extract_text(uploaded_file)
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def calculate_similarity_bert(text1, text2):
    ats_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    embeddings1 = ats_model.encode([text1])
    embeddings2 = ats_model.encode([text2])
    similarity = cosine_similarity(embeddings1, embeddings2)[0][0]
    return similarity

def get_report(resume_and_answer, job_desc):
    client = Groq(api_key=api_key)
    prompt = f"""
    # Context:
    - You are an AI Resume Analyzer, you will be given a candidate's resume + their answer to the open question, and the job description.

    # Instruction:
    - Analyze based on required skills, experience, and qualifications in the job description.
    - Give each relevant point a score out of 5 at the start with an emoji (✅ match, ❌ not match, ⚠️ unclear).
    - End with "Suggestions to improve your application:" followed by clear improvement tips.

    # Inputs:
    Candidate Submission: {resume_and_answer}
    ---
    Job Description: {job_desc}

    # Output:
    - Each any every point should be given a score (example: 6/10 ).
    - If the candicate is not relevant, give score below 5/10
    - Final improvement suggestions.
    """
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

def extract_scores(text):
    pattern = r'(\d+(?:\.\d+)?)/10'
    matches = re.findall(pattern, text)
    return [float(match) for match in matches]

# ===== Form =====
if not st.session_state.form_submitted:
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    with st.form("application_form"):
        resume_file = st.file_uploader("Upload your Resume/CV (PDF)", type="pdf")
        open_question = st.text_area(
            "Tell us why you are matching with this role (max 500 words):",
            max_chars=3000,
            placeholder="Write your answer here..."
        )

        submitted = st.form_submit_button("Submit Application")
        if submitted:
            if resume_file and open_question.strip():
                st.session_state.resume_text = extract_pdf_text(resume_file)
                st.session_state.open_question = open_question
                st.session_state.form_submitted = True
                st.rerun()
            else:
                st.warning("Please upload your CV and fill the open question.")
    st.markdown('</div>', unsafe_allow_html=True)

# ===== Processing =====
if st.session_state.form_submitted:
    combined_text = st.session_state.resume_text + "\n\nOpen Question Answer:\n" + st.session_state.open_question
    score_place = st.info("Calculating similarity score...")
    ats_score = calculate_similarity_bert(combined_text, job_desc)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="score-card">', unsafe_allow_html=True)
        st.write("ATS Similarity Score:")
        st.subheader(f"{ats_score:.4f}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        report_scores = []
        score_place.info("Generating AI evaluation report...")
        report = get_report(combined_text, job_desc)
        report_scores = extract_scores(report)
        avg_score = sum(report_scores) / (10 * len(report_scores)) if report_scores else 0

        st.markdown('<div class="score-card">', unsafe_allow_html=True)
        st.write("Average AI Score:")
        st.subheader(f"{avg_score:.4f}")
        st.markdown('</div>', unsafe_allow_html=True)

    score_place.success("Analysis complete!")

    st.subheader("AI Generated Analysis Report")
    st.markdown(f'<div class="report-box">{report}</div>', unsafe_allow_html=True)

    st.download_button(
        label="Download Report",
        data=report,
        file_name="data_scientist_report.txt",
        icon=":material/download:",
    )

    # ===== Save to CSV =====
    new_data = {
        'username': [username],
        'timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        'bert_score': [round(ats_score, 2)],
        'groq_score': [round(avg_score, 2)],
        'final_score': [round((ats_score + avg_score) / 2, 2)]
    }
    df_new = pd.DataFrame(new_data)
    csv_path = "screening_results_ds.csv"

    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
        try:
            df_existing = pd.read_csv(csv_path)
        except pd.errors.EmptyDataError:
            df_existing = pd.DataFrame(columns=df_new.columns)
    else:
        df_existing = pd.DataFrame(columns=df_new.columns)

    df_final = pd.concat([df_existing, df_new], ignore_index=True)
    df_final.to_csv(csv_path, index=False)
    df_final = df_final.dropna(subset=['final_score'])
    df_final['rank'] = df_final['final_score'].rank(ascending=False, method='min').astype(int)

    st.success(f"Data telah disimpan ke {csv_path}")

    st.subheader("🏆 Top 10 Candidates")
    top_10 = df_final.sort_values('final_score', ascending=False).head(10)
    st.dataframe(
        top_10[['rank', 'username', 'final_score', 'bert_score', 'groq_score', 'timestamp']],
        hide_index=True,
        use_container_width=True
    )

    st.download_button(
        label="📥 Download Top 10 Results",
        data=top_10.to_csv(index=False).encode('utf-8'),
        file_name="top_10_scores_ds.csv",
        mime="text/csv"
    )
