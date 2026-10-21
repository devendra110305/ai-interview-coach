# app.py

import streamlit as st
import tempfile

from resume_parser import extract_resume_text
from skill_extractor import extract_skills
from rag import create_vector_store, generate_question
from evaluator import evaluate_answer

# ==========================================
# 1. PAGE CONFIG & PROFESSIONAL UI/UX
# ==========================================
st.set_page_config(
    page_title="InterviewGPT | AI Coach",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Refined, robust CSS
st.markdown("""
<style>
    /* Hide Streamlit default header/footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Global App Styling */
    .stApp {
        background-color: #0E1117;
        color: #E2E8F0;
    }
    
    /* Typography */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #F8FAFC;
    }
    
    /* Gradient Title */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #6366F1, #A855F7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        padding-bottom: 0;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #94A3B8;
        margin-bottom: 2rem;
    }
    
    /* Skill Badges */
    .skill-badge {
        display: inline-block;
        background-color: rgba(99, 102, 241, 0.15);
        color: #A5B4FC;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 4px;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    /* Custom styled question box */
    .question-box {
        background-color: #0F172A;
        border-left: 4px solid #8B5CF6;
        padding: 1.5rem;
        border-radius: 8px;
        font-size: 1.2rem;
        font-weight: 500;
        color: #F8FAFC;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }
    
    /* Styled Button */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #6366F1 0%, #8B5CF6 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
        color: white !important;
    }
    .stButton > button:disabled {
        background: #334155;
        color: #64748B !important;
        cursor: not-allowed;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. SESSION STATE MANAGEMENT
# ==========================================
if "skills" not in st.session_state:
    st.session_state.skills = []
if "resume_name" not in st.session_state:
    st.session_state.resume_name = None
if "question_pdf_path" not in st.session_state:
    st.session_state.question_pdf_path = None
if "current_question" not in st.session_state:
    st.session_state.current_question = None


# ==========================================
# 3. HEADER SECTION
# ==========================================
st.markdown('<p class="main-title">InterviewGPT 💼</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Personalized AI Interview Coach | Powered by RAG & Groq</p>', unsafe_allow_html=True)


# ==========================================
# 4. UPLOAD PHASE (Using Native Containers)
# ==========================================
col1, col2 = st.columns(2, gap="large")

with col1:
    with st.container(border=True):
        st.markdown("### 📄 Step 1: Candidate Profile")
        st.markdown("Upload your resume to extract technical skills.")
        
        resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"], label_visibility="collapsed")
        
        if resume_file is not None:
            if st.session_state.resume_name != resume_file.name:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(resume_file.read())
                    resume_path = tmp.name
                
                with st.spinner("Extracting skills..."):
                    resume_text = extract_resume_text(resume_path)
                    st.session_state.skills = extract_skills(resume_text)
                    st.session_state.resume_name = resume_file.name
                
            st.success(f"✅ Resume loaded: {resume_file.name}")
            
            if st.session_state.skills:
                st.markdown("**Detected Skills:**")
                badges_html = "".join([f"<span class='skill-badge'>{skill.upper()}</span>" for skill in st.session_state.skills])
                st.markdown(badges_html, unsafe_allow_html=True)
            else:
                st.warning("⚠️ No technical skills detected.")

with col2:
    with st.container(border=True):
        st.markdown("### 📚 Step 2: Knowledge Base")
        st.markdown("Upload the PDF containing interview questions.")
        
        interview_pdf = st.file_uploader("Upload Question Bank (PDF)", type=["pdf"], label_visibility="collapsed")
        
        if interview_pdf is not None:
            if st.session_state.question_pdf_path is None or not st.session_state.question_pdf_path.endswith(interview_pdf.name):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(interview_pdf.read())
                    st.session_state.question_pdf_path = tmp.name
                
            st.success(f"✅ Question Bank loaded: {interview_pdf.name}")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 5. GENERATION PHASE (Constraint Implementation)
# ==========================================
st.markdown("### 🎯 Step 3: Generate Personalized Question")

# Logic constraint: User must upload BOTH files to proceed
if not st.session_state.skills:
    st.info("💡 Please upload your resume first. Your extracted skills will be used to query the RAG system.")
elif not st.session_state.question_pdf_path:
    st.info("💡 Please upload the Interview Questions PDF.")
else:
    if st.button("Generate Personalized Interview Question", use_container_width=True):
        with st.spinner("RAG system analyzing skills and retrieving relevant question..."):
            vectordb = create_vector_store(st.session_state.question_pdf_path)
            
            # Pass extracted skills directly to the RAG generation function
            question = generate_question(vectordb, st.session_state.skills)
            st.session_state.current_question = question
            
        st.rerun()


# ==========================================
# 6. INTERVIEW PHASE (Question & Answer)
# ==========================================
if st.session_state.current_question:
    st.markdown("---")
    st.markdown("### 🎤 Your Interview Question")
    
    # Display the personalized question in a custom styled box
    st.markdown(f"<div class='question-box'>{st.session_state.current_question}</div>", unsafe_allow_html=True)
    
    answer = st.text_area("Your Answer", height=200, placeholder="Type your detailed answer here. Structure it with examples if possible...")
    
    if st.button("Evaluate Answer", use_container_width=True):
        if not answer.strip():
            st.warning("⚠️ Please provide an answer before evaluating.")
        else:
            with st.spinner("Analyzing answer and generating feedback..."):
                feedback = evaluate_answer(st.session_state.current_question, answer)
            
            st.markdown("---")
            st.markdown("### 📊 Evaluation Report")
            
            # Display feedback cleanly inside a native container
            with st.container(border=True):
                st.markdown(feedback)