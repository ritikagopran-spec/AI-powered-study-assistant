import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AI Study Assistant PRO", layout="wide")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

@st.cache_resource
def load_model():
    return genai.GenerativeModel('gemini-3.8-flash')

model = load_model()

with st.sidebar:
    st.title("PRO Controls")
    st.success("✅ PRO Mode - Key Loaded")
    subject = st.selectbox("Subject", ["Maths", "Science", "History", "Computer", "English", "General"])
    mode = st.selectbox("Mode", ["Doubt Solver", "Notes Maker", "Explain Topic", "Quiz Generator"])
    language = st.selectbox("Language", ["English", "Hindi", "Hinglish"])
    if st.button("🗑️ Chat Clear"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Sawal likho... e.g. pythagoras theorem"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            full_text = ""
            placeholder = st.empty()
            final_prompt = f"You are expert {subject} teacher. Mode: {mode}. Language: {language}. Question: {prompt}. If maths, give step-by-step with LaTeX."
            response = model.generate_content(final_prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    placeholder.markdown(full_text + "▌")
            placeholder.markdown(full_text)
            st.session_state.messages.append({"role": "assistant", "content": full_text})
        except Exception as e:
            st.error(f"Error: {e}")
