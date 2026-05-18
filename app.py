import streamlit as st
import time
import random
import re
from datetime import datetime

# Try to import Gemini & prompts, but don't crash
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from prompts import QUESTION_PROMPT, FEEDBACK_PROMPT, SUMMARY_PROMPT
    PROMPTS_AVAILABLE = True
except ImportError:
    PROMPTS_AVAILABLE = False

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="PrepPilot AI",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# THEME INIT
# ---------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    
    theme_choice = st.radio("🎨 Theme", ["Light", "Dark"], horizontal=True)
    if theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        st.rerun()
    
    max_q = st.slider("📋 Number of questions", 3, 10, 5)
    selected_role = st.selectbox("🎯 Interview Role", [
        "Frontend Developer", "Backend Developer", "Full Stack Developer",
        "Data Scientist", "Machine Learning Engineer", "DevOps Engineer",
        "Product Manager", "HR Interview (Behavioral)"
    ])
    
    st.markdown("---")
    st.markdown("### ℹ️ Tips")
    st.caption("• Be specific with examples\n• Use STAR method\n• Feedback appears instantly")

# ---------------------------------------------------
# APPLY THEME CSS (hide top bar & deploy button)
# ---------------------------------------------------
if st.session_state.theme == "Dark":
    st.markdown("""
    <style>
    header, .stDeployButton, .stToolbar, .stAppHeader {
        display: none !important;
    }
    .main .block-container {
        padding-top: 1rem;
    }
    html, body, .stApp {
        background-color: #0f172a !important;
        color: #f1f5f9 !important;
    }
    .stTextArea textarea, .stSelectbox div, .stSlider, .stButton button {
        background-color: #1e293b !important;
        color: white !important;
        border-color: #334155 !important;
    }
    .stButton button {
        background-color: #f97316 !important;
    }
    .question-card {
        background-color: #1e293b !important;
        border-left-color: #f97316 !important;
        color: white !important;
    }
    .question-card p {
        font-size: 1.4rem !important;
        font-weight: bold !important;
        line-height: 1.5 !important;
    }
    .feedback-card {
        background-color: #2d1a0f !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    header, .stDeployButton, .stToolbar, .stAppHeader {
        display: none !important;
    }
    .main .block-container {
        padding-top: 1rem;
    }
    html, body, .stApp {
        background-color: #f5f7fb !important;
        color: #1f2937 !important;
    }
    .stTextArea textarea, .stSelectbox div, .stSlider {
        background-color: white !important;
        color: black !important;
    }
    .question-card {
        background-color: white !important;
        color: black !important;
        border-left: 5px solid #ff4b4b;
    }
    .question-card p {
        font-size: 1.4rem !important;
        font-weight: bold !important;
        line-height: 1.5 !important;
    }
    .feedback-card {
        background-color: #eef4ff !important;
        color: black !important;
    }
    .stButton button {
        background-color: #ff4b4b !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------
# INITIALIZE GEMINI (if possible)
# ---------------------------------------------------
USE_GEMINI = False
gemini_model = None

if GEMINI_AVAILABLE and PROMPTS_AVAILABLE:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            for model_name in ["gemini-1.5-flash", "gemini-pro", "models/gemini-pro"]:
                try:
                    test_model = genai.GenerativeModel(model_name)
                    test_model.generate_content("test")
                    gemini_model = test_model
                    USE_GEMINI = True
                    break
                except:
                    continue
    except:
        pass

# Show mode indicator in sidebar
if USE_GEMINI:
    st.sidebar.success("🤖 AI Mode: Gemini (Live)")
else:
    st.sidebar.info("📝 AI Mode: Smart Fallback (Rules-based)")

# ---------------------------------------------------
# FALLBACK QUESTION BANK & FUNCTIONS
# ---------------------------------------------------
QUESTION_BANKS = {
    "Frontend Developer": [
        "Explain the difference between let, const, and var in JavaScript.",
        "What is the virtual DOM and how does React use it?",
        "How would you optimize a website's loading speed?",
        "Describe your experience with responsive design.",
        "What are closures in JavaScript? Give an example."
    ],
    "Backend Developer": [
        "What is the difference between SQL and NoSQL databases?",
        "Explain RESTful API design principles.",
        "How would you handle authentication in a web app?",
        "What is the purpose of indexing in databases?",
        "Describe a time you optimized a slow database query."
    ],
    "Full Stack Developer": [
        "Describe a full-stack project you worked on from start to finish.",
        "How do you decide between server-side rendering and client-side rendering?",
        "What tools do you use for debugging both frontend and backend?",
        "Explain how the browser sends a request to the server and gets a response.",
        "How do you manage environment variables across development and production?"
    ],
    "Data Scientist": [
        "Explain the bias-variance tradeoff.",
        "What is overfitting and how do you prevent it?",
        "Describe a data cleaning project you worked on.",
        "What is the difference between supervised and unsupervised learning?",
        "How do you handle missing data in a dataset?"
    ],
    "Machine Learning Engineer": [
        "What is the difference between batch and stochastic gradient descent?",
        "How do you choose the right evaluation metric for a classification problem?",
        "Explain the concept of transfer learning.",
        "What is a confusion matrix and what can you learn from it?",
        "How do you deploy a machine learning model into production?"
    ],
    "DevOps Engineer": [
        "What is CI/CD and why is it important?",
        "Explain the difference between containers and virtual machines.",
        "How do you monitor the health of a production system?",
        "What is Infrastructure as Code? Give examples.",
        "How do you handle secrets in a cloud environment?"
    ],
    "Product Manager": [
        "How do you prioritize features for a product roadmap?",
        "Tell me about a time you had to make a product decision with incomplete data.",
        "How do you gather and incorporate user feedback?",
        "What metrics would you track for a new feature?",
        "Describe your process for writing product requirements."
    ],
    "HR Interview (Behavioral)": [
        "Tell me about yourself.",
        "What is your greatest strength and weakness?",
        "Why do you want to work here?",
        "Describe a time you faced a conflict at work and how you resolved it.",
        "Where do you see yourself in five years?"
    ]
}
DEFAULT_QUESTIONS = [
    "Tell me about yourself.",
    "What is your greatest strength?",
    "Describe a challenge you overcame.",
    "Why are you interested in this role?",
    "Where do you see yourself in five years?"
]

def fallback_generate_question(role, history):
    asked = [h["question"] for h in history]
    bank = QUESTION_BANKS.get(role, DEFAULT_QUESTIONS)
    available = [q for q in bank if q not in asked]
    return random.choice(available) if available else random.choice(bank)

def fallback_evaluate_answer(question, answer):
    ans_len = len(answer.strip())
    if ans_len < 20:
        rating = 3
        feedback = f"""✅ Positive Points: You attempted to answer.
❌ Negative Points: Answer is very short ({ans_len} characters). Lacks details.
💡 Improvement Suggestions: Elaborate more – aim for 2-3 sentences. Use STAR method.
🎯 Rating: {rating}/10"""
    elif ans_len < 50:
        rating = 5
        feedback = f"""✅ Positive Points: You provided a relevant answer.
❌ Negative Points: Could include more specific examples.
💡 Improvement Suggestions: Add concrete details from your experience.
🎯 Rating: {rating}/10"""
    else:
        keywords = ["example", "project", "experience", "team", "problem", "solve", "develop"]
        score = sum(1 for kw in keywords if kw in answer.lower())
        rating = 8 if score >= 2 else 6
        if rating == 8:
            feedback = f"""✅ Positive Points: Good length and detail. You included examples.
❌ Negative Points: Could be even more structured.
💡 Improvement Suggestions: Practice framing answers with Situation, Task, Action, Result.
🎯 Rating: {rating}/10"""
        else:
            feedback = f"""✅ Positive Points: Detailed answer.
❌ Negative Points: Could add more concrete examples or metrics.
💡 Improvement Suggestions: Quantify achievements (e.g., 'improved performance by 20%').
🎯 Rating: {rating}/10"""
    return {"feedback": feedback, "rating": rating}

def fallback_generate_summary(role, history):
    if not history:
        return "No interview data available."
    avg_rating = sum(t["rating"] for t in history) / len(history)
    strengths = []
    improvements = []
    long_answers = sum(1 for t in history if len(t["answer"]) > 80)
    if long_answers >= len(history)/2:
        strengths.append("You provided detailed answers.")
    else:
        improvements.append("Give more detailed answers (2-3 sentences).")
    if any(len(t["answer"]) < 30 for t in history):
        improvements.append("Some answers were too brief – use examples.")
    else:
        strengths.append("You maintained good answer length.")
    if avg_rating >= 7:
        strengths.append(f"Your answers were rated well (average {avg_rating:.1f}/10).")
    elif avg_rating >= 5:
        improvements.append(f"Your average rating is {avg_rating:.1f}/10 – focus on adding specific experiences.")
    else:
        improvements.append(f"Your average rating is {avg_rating:.1f}/10 – practice structuring answers with STAR.")
    if not strengths:
        strengths.append("You completed the interview – that's a great start!")
    if not improvements:
        improvements.append("Keep practicing with different question types.")
    return f"""**Overall Performance:** Average rating {avg_rating:.1f}/10

**Strengths:**
{chr(10).join('- ' + s for s in strengths)}

**Areas to Improve:**
{chr(10).join('- ' + s for s in improvements)}

**Tips for Next Time:**
- Use the STAR method (Situation, Task, Action, Result)
- Quantify achievements when possible
- Practice answering out loud
- Review your transcript to identify weak spots"""

# ---------------------------------------------------
# GEMINI FUNCTIONS (used when available)
# ---------------------------------------------------
def gemini_generate_question(role, history):
    asked = [h["question"] for h in history]
    prompt = QUESTION_PROMPT.format(role=role, history=str(asked))
    try:
        resp = gemini_model.generate_content(prompt)
        q = resp.text.strip().strip('"')
        if q and q not in asked:
            return q
    except:
        pass
    return fallback_generate_question(role, history)

def gemini_evaluate_answer(question, answer):
    prompt = FEEDBACK_PROMPT.format(question=question, answer=answer)
    try:
        resp = gemini_model.generate_content(prompt)
        txt = resp.text.strip()
        rating_match = re.search(r'Rating:\s*(\d+)/10', txt)
        rating = int(rating_match.group(1)) if rating_match else 5
        return {"feedback": txt, "rating": rating}
    except:
        return fallback_evaluate_answer(question, answer)

def gemini_generate_summary(role, history):
    log = ""
    for i, t in enumerate(history, 1):
        log += f"Q{i}: {t['question']}\nA{i}: {t['answer']}\nFeedback: {t['feedback']}\n\n"
    prompt = SUMMARY_PROMPT.format(role=role, full_log=log)
    try:
        resp = gemini_model.generate_content(prompt)
        return resp.text.strip()
    except:
        return fallback_generate_summary(role, history)

# ---------------------------------------------------
# WRAPPER FUNCTIONS (choose Gemini or fallback)
# ---------------------------------------------------
def generate_question(role, history):
    if USE_GEMINI and gemini_model:
        return gemini_generate_question(role, history)
    return fallback_generate_question(role, history)

def evaluate_answer(question, answer):
    if USE_GEMINI and gemini_model:
        return gemini_evaluate_answer(question, answer)
    return fallback_evaluate_answer(question, answer)

def generate_summary(role, history):
    if USE_GEMINI and gemini_model:
        return gemini_generate_summary(role, history)
    return fallback_generate_summary(role, history)

# ---------------------------------------------------
# SESSION STATE INIT
# ---------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = "role_selection"
    st.session_state.role = None
    st.session_state.history = []
    st.session_state.current_question = None
    st.session_state.max_questions = max_q

st.session_state.max_questions = max_q

# ---------------------------------------------------
# MAIN UI (no top header)
# ---------------------------------------------------
# Step 1: Role selection
if st.session_state.step == "role_selection":
    st.markdown(f"**Selected Role:** {selected_role}")
    if st.button("🚀 Start Interview", use_container_width=True):
        st.session_state.role = selected_role
        with st.spinner("Preparing first question..."):
            st.session_state.current_question = generate_question(selected_role, [])
        st.session_state.step = "interviewing"
        st.rerun()

# Step 2: Interview
elif st.session_state.step == "interviewing":
    st.markdown(f"## 🎯 Role: {st.session_state.role}")
    current_q_num = len(st.session_state.history) + 1
    st.progress(len(st.session_state.history)/st.session_state.max_questions, text=f"Question {current_q_num} of {st.session_state.max_questions}")
    
    st.markdown(f"<div class='question-card'><h3>Interviewer</h3><p>{st.session_state.current_question}</p></div>", unsafe_allow_html=True)
    
    answer_key = f"answer_{current_q_num}"
    user_answer = st.text_area("Your Answer", height=180, placeholder="Type your answer here...", key=answer_key)
    
    if st.button("Submit Answer", type="primary", use_container_width=True):
        if not user_answer.strip():
            st.warning("Please enter an answer.")
        else:
            with st.spinner("Analyzing your answer..."):
                eval_result = evaluate_answer(st.session_state.current_question, user_answer)
                st.session_state.history.append({
                    "question": st.session_state.current_question,
                    "answer": user_answer,
                    "feedback": eval_result["feedback"],
                    "rating": eval_result["rating"]
                })
                if answer_key in st.session_state:
                    del st.session_state[answer_key]
                
                st.markdown(f"**Rating:** {eval_result['rating']}/10")
                st.progress(eval_result['rating']/10)
                st.markdown(f"<div class='feedback-card'>{eval_result['feedback']}</div>", unsafe_allow_html=True)
                time.sleep(1)
                if len(st.session_state.history) >= st.session_state.max_questions:
                    st.session_state.step = "finished"
                else:
                    with st.spinner("Generating next question..."):
                        st.session_state.current_question = generate_question(st.session_state.role, st.session_state.history)
                st.rerun()
    
    if st.session_state.history:
        last = st.session_state.history[-1]
        st.markdown("### 📌 Last Answer Feedback")
        st.info(last["feedback"])
        stars = "⭐" * int(last["rating"]//2) + "☆" * (5 - int(last["rating"]//2))
        st.caption(f"Rating: {stars} ({last['rating']}/10)")
    
    if st.button("⏹️ End Interview & Get Summary", use_container_width=True):
        st.session_state.step = "finished"
        st.rerun()

# Step 3: Final report
elif st.session_state.step == "finished":
    st.markdown("## 📊 Interview Completed")
    col1, col2 = st.columns(2)
    col1.metric("Role", st.session_state.role)
    col2.metric("Questions Answered", len(st.session_state.history))
    
    if st.button("📝 Generate Final Report", type="primary", use_container_width=True):
        with st.spinner("Generating report..."):
            summary = generate_summary(st.session_state.role, st.session_state.history)
            st.markdown("## 📝 Final AI Report")
            st.success(summary)
            with st.expander("📋 Full Interview Transcript"):
                for i, turn in enumerate(st.session_state.history, 1):
                    st.markdown(f"### Q{i}: {turn['question']}")
                    st.markdown(f"**Your Answer:** {turn['answer']}")
                    st.markdown(f"**AI Feedback:** {turn['feedback']}")
                    st.markdown(f"**Rating:** {turn['rating']}/10")
                    st.divider()
            # Export
            report_text = f"""PrepPilot AI Interview Report
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Role: {st.session_state.role}
Questions: {len(st.session_state.history)}

FINAL SUMMARY:
{summary}

--- Full Transcript ---
"""
            for i, turn in enumerate(st.session_state.history, 1):
                report_text += f"\nQ{i}: {turn['question']}\nAnswer: {turn['answer']}\nFeedback: {turn['feedback']}\nRating: {turn['rating']}/10\n---\n"
            st.download_button(
                label="💾 Download Report (.txt)",
                data=report_text,
                file_name=f"preppilot_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    if st.button("🔄 Start New Interview", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()