import nltk
nltk.download('punkt')
nltk.download('punkt_tab')

import streamlit as st
import fitz  # PyMuPDF
from nltk.tokenize import sent_tokenize
import random
import nltk
import os

# --- Ensure NLTK data is present ---
nltk_data_dir = os.path.join(os.path.expanduser("~"), "nltk_data")
required = ["punkt", "punkt_tab"]
for pkg in required:
    try:
        nltk.data.find(f"tokenizers/{pkg}")
    except LookupError:
        nltk.download(pkg)

# Streamlit Page Config
st.set_page_config(page_title="AI Quiz Generator", page_icon="🧠", layout="wide")

# Title
st.title("🧠 AI Quiz Generator - IILM")
st.write("Upload a PDF and let AI generate a fun multiple-choice quiz from it!")

# Upload PDF
uploaded_file = st.file_uploader("📄 Upload your PDF file", type=["pdf"])

# Extract text from PDF
def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as pdf:
        for page in pdf:
            text += page.get_text("text") + "\n"
    return text

# Generate MCQs
def generate_mcqs(text, num_questions=5):
    sentences = sent_tokenize(text)
    sentences = [s.strip() for s in sentences if len(s.split()) > 6]
    if not sentences:
        return []
    selected_sentences = random.sample(sentences, min(num_questions, len(sentences)))
    questions = []
    for s in selected_sentences:
        words = [w for w in s.split() if any(c.isalnum() for c in w)]
        if len(words) > 6:
            answer = random.choice(words)
            question = s.replace(answer, "______", 1)
            options = random.sample(words, min(4, len(words)))
            if answer not in options:
                options[random.randint(0, len(options)-1)] = answer
            random.shuffle(options)
            questions.append((question, options, answer))
    return questions

# Main logic
if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)
    if not text.strip():
        st.error("Uploaded PDF contained no extractable text. Try a different PDF.")
    else:
        st.success("✅ PDF uploaded and processed successfully!")
        num_questions = st.number_input("🔢 How many questions do you want to generate?", min_value=1, max_value=20, value=5)

        if st.button("🚀 Generate Quiz"):
            mcqs = generate_mcqs(text, num_questions=num_questions)

            if not mcqs:
                st.warning("⚠️ Could not generate questions. Try uploading a longer or more detailed PDF.")
            else:
                st.session_state["quiz"] = mcqs
                st.session_state["answers"] = {}

# If quiz already generated
if "quiz" in st.session_state:
    st.subheader("📚 Your Quiz is Ready!")

    for i, (q, options, ans) in enumerate(st.session_state["quiz"], 1):
        selected = st.radio(f"**Q{i}.** {q}", options, key=f"q{i}")
        st.session_state["answers"][i] = {"selected": selected, "correct": ans}

    if st.button("✅ Submit All"):
        score = 0
        for i, data in st.session_state["answers"].items():
            if data["selected"] == data["correct"]:
                score += 1
        st.success(f"🏁 Final Score: **{score}/{len(st.session_state['answers'])}**")
        st.info("✨ Thanks for using this AI-powered Quiz Generator by **Gaurav Yadav [1CSE17]** ✨")
        del st.session_state["quiz"]
