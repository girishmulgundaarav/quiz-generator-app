import streamlit as st
import openai

from quiz_generator import generate_quiz
from database import create_table, save_history, get_history
from utils import shuffle_questions, start_timer
from pdf_export import create_pdf
from docx_export import create_docx


# -------------------------------------------------------
# INITIAL SETUP
# -------------------------------------------------------
openai.api_key = st.secrets["OPENAI_API_KEY"]
create_table()

st.set_page_config(page_title="AI Quiz Generator", page_icon="🧩")
st.title("🧩 AI Quiz Generator")


# -------------------------------------------------------
# GLOBAL CSS
# -------------------------------------------------------
st.markdown("""
<style>

body, html {
    background: #f7f9fb;
}

@keyframes fadeInCard {
    0% { opacity: 0; transform: translateY(10px); }
    100% { opacity: 1; transform: translateY(0px); }
}

/* Timer Button */
.timer-button {
    background: #ff4757;
    color: white;
    padding: 10px 22px;
    border-radius: 30px;
    font-size: 20px;
    font-weight: 600;
    text-align: center;
    margin-top: 10px;
    display: block;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.15);
    animation: pulse 1.5s infinite ease-in-out;
}

@keyframes pulse {
    0%   { transform: scale(1);   }
    50%  { transform: scale(1.07);}
    100% { transform: scale(1);   }
}

/* Hide Streamlit UI */
button[title="View app menu"] { display: none !important; }
header, footer, #MainMenu {visibility: hidden;}

</style>
""", unsafe_allow_html=True)



# -------------------------------------------------------
# SIDEBAR SETTINGS
# -------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Quiz Settings")

    mode = st.radio("Mode", ["Student Mode", "Teacher Mode"])
    num_q = st.slider("Number of Questions", 5, 20, 5)

    timer_enabled = st.checkbox("Enable Timer?")
    seconds = st.slider("Timer (seconds)", 30, 600, 120) if timer_enabled else 0

    st.markdown("---")
    st.caption("Customize your quiz settings here.")



# -------------------------------------------------------
# TOPIC INPUT
# -------------------------------------------------------
topic = st.text_input("Enter Topic")

if st.button("Generate Quiz"):

    if not topic.strip():
        st.error("Please enter a topic!")
    else:
        with st.spinner("Generating quiz..."):

            quiz = generate_quiz(topic, mode, num_q)
            quiz = shuffle_questions(quiz)

            st.session_state.quiz = quiz
            st.session_state.topic = topic
            st.session_state.difficulty = mode
            st.session_state.mode = mode

            # Timer state
            st.session_state.timer_enabled = timer_enabled
            st.session_state.seconds = seconds
            st.session_state.timer_running = timer_enabled

            # Remove old remaining time
            if "remaining" in st.session_state:
                del st.session_state["remaining"]

            # Reset answers
            st.session_state.user_answers = {}

            # Reset submit flags
            st.session_state.submitted = False
            st.session_state.submit_pressed = False

        st.success("🎉 Quiz Ready!")



# Stop if quiz is not generated yet
if "quiz" not in st.session_state:
    st.stop()



# ======================================================================
# =========================== TEACHER MODE ==============================
# ======================================================================
if st.session_state.mode == "Teacher Mode":

    st.header("📄 Teacher Mode — Download Quiz")

    c1, c2 = st.columns(2)

    with c1:
        pdf_path = create_pdf(st.session_state.quiz,
                              st.session_state.topic,
                              st.session_state.difficulty)
        with open(pdf_path, "rb") as f:
            st.download_button("📄 Download PDF", f, "quiz.pdf")

    with c2:
        doc_path = create_docx(st.session_state.quiz,
                               st.session_state.topic,
                               st.session_state.difficulty)
        with open(doc_path, "rb") as f:
            st.download_button("📘 Download DOCX", f, "quiz.docx")

    st.stop()



# ======================================================================
# =========================== STUDENT MODE ==============================
# ======================================================================

st.header("📘 Student Quiz")

# ⭐⭐ TIMER RENDERED FROM MAIN (Displays in Sidebar)
if st.session_state.get("timer_enabled", False):
    start_timer(st.session_state.seconds)


# Ensure answers dict exists
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}



# -------------------------------------------------------
# RENDER QUESTIONS AS HTML CARDS
# -------------------------------------------------------
for idx, q in enumerate(st.session_state.quiz):

    st.markdown(f"""
    <div style="
        background: white;
        padding: 20px 22px;
        border-radius: 18px;
        margin-top: 22px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.10);
        border: 1px solid rgba(0,0,0,0.07);
        animation: fadeInCard 0.4s ease;
    ">
        <h3 style="margin-top:0; margin-bottom:0;">
            {idx+1}. {q['question']}
        </h3>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.user_answers[idx] = st.radio(
        "",
        q["options"],
        key=f"ans_{idx}"
    )



# ======================================================================
# SUBMIT LOGIC (FINAL FIX)
# ======================================================================

# --- Initialize submit_pressed if missing ---
if "submit_pressed" not in st.session_state:
    st.session_state.submit_pressed = False


# --- Safe Time-Up Condition (fixed) ---
time_up = (
    st.session_state.get("timer_enabled", False)
    and not st.session_state.get("timer_running", True)
    and not st.session_state.get("submitted", False)
    and not st.session_state.get("submit_pressed", False)  # ⭐ CRITICAL FIX
)

if time_up:
    st.error("⏳ Time is up — You cannot submit answers.")
    st.button("Submit Quiz", disabled=True)

else:

    # --- SUBMIT BUTTON ---
    if st.button("Submit Quiz"):

        # ⭐ MUST BE FIRST → prevents Time's Up firing
        st.session_state.submit_pressed = True
        st.session_state.submitted = True

        # Stop timer
        st.session_state.timer_running = False
        st.session_state.remaining = 0
        st.query_params = {}

        # ---- SCORE QUIZ ----
        correct = 0

        for i, q in enumerate(st.session_state.quiz):
            selected = st.session_state.user_answers.get(i, "")
            options = q["options"]

            # Convert option → A/B/C/D
            if selected in options:
                index = options.index(selected)
                selected_letter = ["A", "B", "C", "D"][index]
            else:
                selected_letter = ""

            if selected_letter.upper() == q["answer"].upper():
                correct += 1

        save_history(
            st.session_state.topic,
            st.session_state.difficulty,
            correct,
            len(st.session_state.quiz)
        )

        st.success(f"🎉 Your Score: {correct}/{len(st.session_state.quiz)}")

        st.write("### Correct Answers")
        for i, q in enumerate(st.session_state.quiz):
            st.write(f"**{i+1}. {q['answer']}** — {q['explanation']}")


# ======================================================================
# HISTORY
# ======================================================================
st.write("---")
st.subheader("📊 Quiz History")

for topic, diff, score, total, ts in get_history():
    st.write(f"📌 **{topic}** ({diff}) — {score}/{total} — *{ts}*")
