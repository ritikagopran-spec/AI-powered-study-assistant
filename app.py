import streamlit as st
import google.generativeai as genai
import time
from google.api_core import exceptions

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Study Assistant PRO", page_icon="📚", layout="wide")

# --- API SETUP ---
# Streamlit Secrets se key lega
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("API Key nahi mili! Streamlit Cloud > Secrets me GEMINI_API_KEY daalo")
    st.stop()

# --- FAST MODEL LOADING (Cache se fast hoga) ---
@st.cache_resource
def load_model():
    return genai.GenerativeModel('gemini-1.5-flash')

model = load_model()

# --- RETRY FUNCTION (RateLimit ka permanent fix) ---
def get_response_with_retry(prompt):
    for attempt in range(3):
        try:
            # Streaming for speed
            response = model.generate_content(prompt, stream=True)
            full_text = ""
            placeholder = st.empty()
            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    placeholder.markdown(full_text + "▌")
            placeholder.markdown(full_text)
            return full_text
        except exceptions.ResourceExhausted:
            st.warning(f"⚠️ API busy hai, {10*(attempt+1)} sec wait kar raha hu... ({attempt+1}/3)")
            time.sleep(10 * (attempt+1))
        except Exception as e:
            st.error(f"Error: {e}")
            return None
    st.error("❌ Limit khatam! 1-2 minute baad try karo. Ya nayi API Key banao.")
    return None

# --- SIDEBAR (Tumhara PRO Controls) ---
with st.sidebar:
    st.title("PRO Controls")
    st.success("✅ PRO Mode - Key Loaded")

    subject = st.selectbox("Subject", ["Maths", "Science", "History", "Computer", "English", "General"])
    mode = st.selectbox("Mode", ["Doubt Solver", "Notes Maker", "Explain Topic", "Quiz Generator"])
    language = st.selectbox("Language", ["English", "Hindi", "Hinglish"])
    
    if st.button("🗑️ Chat Clear"):
        st.session_state.messages = []
        st.rerun()

# --- CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- MAIN PROMPT LOGIC (Sab Subjects ke liye) ---
if prompt := st.chat_input("Sawal likho... (e.g. pythagoras theorem)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Final prompt banayenge subject ke hisab se
    if subject == "Maths":
        final_prompt = f"""
        You are an expert {subject} teacher. Language: {language}. Mode: {mode}.
        Question: {prompt}
        INSTRUCTIONS FOR MATHS:
        1. Pehle Formula likho in LaTeX: $...$
        2. Step-by-step solution do (Step 1, Step 2...)
        3. Har step ko simple bhasha me samjhao
        4. Final Answer ko bold me likho
        5. Agar Notes Maker mode hai to short notes + example do
        """
    else:
        final_prompt = f"""
        You are an expert {subject} teacher. Language: {language}. Mode: {mode}.
        Question: {prompt}
        INSTRUCTIONS:
        1. Answer ko {language} me do
        2. Agar Mode 'Notes Maker' hai to bullet points me notes banao
        3. Agar Mode 'Explain Topic' hai to easy example se samjhao
        4. Agar Mode 'Quiz Generator' hai to 5 MCQs banao
        5. Answer ko neat aur clean formatting me do
        """

    with st.chat_message("assistant"):
        answer = get_response_with_retry(final_prompt)
        if answer:
            st.session_state.messages.append({"role": "assistant", "content": answer})
