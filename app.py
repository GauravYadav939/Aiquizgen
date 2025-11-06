import nltk
# explicit downloads you asked for
nltk.download('punkt')
nltk.download('punkt_tab')

import streamlit as st
import fitz  # PyMuPDF
from nltk.tokenize import sent_tokenize
import random
import os

# --- Ensure NLTK data is present (fallback) ---
nltk_data_dir = os.path.join(os.path.expanduser("~"), "nltk_data")
required = ["punkt", "punkt_tab"]
for pkg in required:
    try:
        nltk.data.find(f"tokenizers/{pkg}")
    except LookupError:
        nltk.download(pkg)

# Streamlit Page Config (no emojis, professional)
st.set_page_config(
    page_title="AI Quiz Generator - IILM",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS Styling ---
st.markdown("""
    <style>
        /* Global Styles */
        body {
            background-color: #f9f9f9;
            color: #1a1a1a;
            font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        }

        /* Title */
        .title {
            text-align: center;
            font-size: 2.2rem;
            font-weight: 600;
            color: #222;
            margin-bottom: 0.2rem;
        }

        /* Subtitle */
        .subtitle {
            text-align: center;
            color: #555;
            font-size: 1.0rem;
            margin-bottom: 1.5rem;
        }

        /* Upload Section */
        .upload-section {
            background-color: #ffffff;
            padding: 22px;
            border-radius: 10px;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
            margin-bottom: 1.6rem;
        }

        /* Button */
        div.stButton > button {
            width: 100%;
            background-color: #0b69ff;
            color: white;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            padding: 10px 0;
            transition: transform 0.08s ease-in-out, box-shadow 0.08s;
        }
        div.stButton > button:active {
            transform: translateY(1px);
        }

        /* Radio labels */
        .stRadio > label, .stRadio > div {
            color: #222;
        }

        /* Result */
        .result {
            font-size: 1.05rem;
            text-align: center;
            padding: 12px;
            border-radius: 8px;
            background: #eef4ff;
            color: #0b3f9a;
            margin-top: 12px;
        }

        /* Footer credit */
        .credit {
            text-align: center;
            color: #6b7280;
            font-size: 0.95rem;
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("<div class='title'>AI Quiz Generator</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Upload a PDF to generate multiple-choice questions automatically.</div>", unsafe_allow_html=True)

# --- Upload PDF ---
st.markdown("<div class='upload-section'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
st.markdown("</div>", unsafe_allow_html=True)

# --- Extract text from PDF ---
def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as pdf:
        for page in pdf:
            text += page.get_text("text") + "\n"
    return text

# --- Generate MCQs ---
def generate_mcqs(text, num_questions=5):
    sentences = sent_tokenize(text)
    sentences = [s.strip() for s in sentences if len(s.split()) > 6]
    if not sentences:
        return []
    selected_sentences = random.sample(sentences, min(num_questions, len(sentences)))
    questions = []
    for s in selected_sentences:
        words = [w.strip(".,;:()[]\"'") for w in s.split() if any(c.isalnum() for c in w)]
        # keep meaningful words only
        words = [w for w in words if len(w) > 2]
        if len(words) >= 4:
            answer = random.choice(words)
            question = s.replace(answer, "______", 1)
            # build distractors from other words, ensure answer is present
            options = random.sample(words, min(4, len(words)))
            if answer not in options:
                options[random.randint(0, len(options) - 1)] = answer
            random.shuffle(options)
            questions.append((question, options, answer))
    return questions

# --- Main Logic ---
if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)
    if not text.strip():
        st.error("No extractable text found in the uploaded PDF. Try a different file.")
    else:
        st.success("PDF uploaded and processed successfully.")
        num_questions = st.number_input("Number of questions to generate", min_value=1, max_value=20, value=5)

        if st.button("Generate Quiz"):
            mcqs = generate_mcqs(text, num_questions=num_questions)
            if not mcqs:
                st.warning("Could not generate questions. Try uploading a more detailed PDF.")
            else:
                st.session_state["quiz"] = mcqs
                st.session_state["answers"] = {}

# --- Quiz Section ---
if "quiz" in st.session_state:
    st.subheader("Generated Quiz")

    for i, (q, options, ans) in enumerate(st.session_state["quiz"], 1):
        selected = st.radio(f"Q{i}. {q}", options, key=f"q{i}")
        st.session_state["answers"][i] = {"selected": selected, "correct": ans}

    if st.button("Submit Answers"):
        score = 0
        for i, data in st.session_state["answers"].items():
            if data["selected"] == data["correct"]:
                score += 1
        st.markdown(f"<div class='result'>Final Score: <b>{score}/{len(st.session_state['answers'])}</b></div>", unsafe_allow_html=True)
        st.markdown("<div class='credit'>Created by <b>Gaurav Yadav [1CSE17]</b></div>", unsafe_allow_html=True)
        del st.session_state["quiz"]
