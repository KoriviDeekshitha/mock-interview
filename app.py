import streamlit as st
from groq import Groq

st.set_page_config(page_title="Mock Interview System", page_icon="🎤")
st.title("🎤 AI Mock Interview System")
st.caption("Practice interviews and get instant AI feedback!")

api_key = st.sidebar.text_input("Enter your Groq API Key", type="password")

# Job roles to choose from
job_roles = [
    "TCS NQT - Fresher",
    "Software Engineer",
    "Data Analyst",
    "AI/ML Engineer",
    "Web Developer",
    "QA Tester"
]

# Initialize session state
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "interview_done" not in st.session_state:
    st.session_state.interview_done = False

# Job role selection
if not st.session_state.interview_started:
    st.subheader("👇 Select a Job Role to Start")
    selected_role = st.selectbox("Choose your job role:", job_roles)

    if st.button("Start Interview 🚀"):
        if not api_key:
            st.warning("⚠️ Please enter your Groq API key in the sidebar!")
        else:
            st.session_state.interview_started = True
            st.session_state.selected_role = selected_role
            st.session_state.messages = [
                {
                    "role": "system",
                    "content": f"""You are an expert interviewer conducting a job interview for {selected_role} position.

Your job is to:
1. Ask ONE interview question at a time
2. Wait for the candidate's answer
3. Give brief feedback on their answer (2-3 lines)
4. Give a score out of 10 for that answer
5. Then ask the next question

After 5 questions, say "INTERVIEW COMPLETE" and give:
- Overall score out of 50
- Strengths
- Areas to improve
- Final verdict (Ready/Almost Ready/Need More Preparation)

Start by greeting the candidate and asking the first question.
Keep questions relevant to {selected_role} role."""
                }
            ]

            # Get first question from AI
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages
            )
            first_question = response.choices[0].message.content
            st.session_state.messages.append({
                "role": "assistant",
                "content": first_question
            })
            st.rerun()

# Interview in progress
if st.session_state.interview_started and not st.session_state.interview_done:
    st.subheader(f"🎯 Interview for: {st.session_state.selected_role}")
    st.progress(st.session_state.question_count / 5)
    st.caption(f"Question {st.session_state.question_count} of 5")

    # Show chat history
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(msg["content"])
                if "INTERVIEW COMPLETE" in msg["content"]:
                    st.session_state.interview_done = True
        elif msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])

    # User answer input
    if not st.session_state.interview_done:
        user_answer = st.chat_input("Type your answer here...")

        if user_answer:
            st.session_state.messages.append({
                "role": "user",
                "content": user_answer
            })
            st.session_state.question_count += 1

            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages
            )
            ai_response = response.choices[0].message.content
            st.session_state.messages.append({
                "role": "assistant",
                "content": ai_response
            })
            st.rerun()

# Interview complete
if st.session_state.interview_done:
    st.balloons()
    st.success("🎉 Interview Complete! Check your feedback above!")
    if st.button("Start New Interview 🔄"):
        st.session_state.interview_started = False
        st.session_state.messages = []
        st.session_state.question_count = 0
        st.session_state.interview_done = False
        st.rerun()