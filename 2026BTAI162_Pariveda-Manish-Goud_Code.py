import streamlit as st
import requests
from PyPDF2 import PdfReader

st.set_page_config(page_title="AI Research Paper Summarizer", page_icon="📄", layout="wide")
st.title("📄 AI Research Paper Summarizer")
st.markdown("Upload any research paper and get a smart, structured summary in seconds.")

st.subheader("🔑 Step 1: Enter Your Gemini API Key")
api_key = st.text_input("Enter Gemini API Key to continue", type="password", placeholder="Paste your API key here")

if not api_key:
    st.warning("👆 Please enter your Gemini API Key first to unlock the app.")
    st.stop()

st.success("API Key Connected ✅")
st.divider()

st.subheader("🤖 Step 2: Choose Model")
model_choice = st.selectbox("Select Gemini Model", ["Gemini 3.5 Flash", "Gemini 3.1 Flash", "Gemini 3.1 Flash Lite"])
model_map = {"Gemini 3.5 Flash": "gemini-2.5-flash", "Gemini 3.1 Flash": "gemini-2.5-flash", "Gemini 3.1 Flash Lite": "gemini-2.5-flash-lite"}
selected_model_id = model_map[model_choice]
summary_type = st.selectbox("Choose Summary Type", ["Detailed", "Short (TL;DR Style)", "Bullet Points"])
st.divider()

def call_gemini(api_key, model_id, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(url, json=data, timeout=60)
    if response.status_code == 200:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    else:
        raise Exception(f"API Error {response.status_code}: {response.text[:300]}")

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

uploaded_file = st.file_uploader("📤 Step 3: Upload Research Paper (PDF)", type=["pdf"])
if uploaded_file is not None:
    st.success(f"Uploaded: {uploaded_file.name}")
    if st.button("✨ Summarize Paper", type="primary", use_container_width=True):
        with st.spinner(f"Generating summary using {model_choice}..."):
            try:
                paper_text = extract_text_from_pdf(uploaded_file)[:15000]
                if len(paper_text) < 200:
                    st.error("Could not extract text from this PDF. Try another paper.")
                else:
                    if summary_type == "Short (TL;DR Style)":
                        instruction = "Give a very short summary in under 150 words. Include TL;DR, Problem, and Main Result only."
                    elif summary_type == "Bullet Points":
                        instruction = "Give summary ONLY in bullet points. 10-12 crisp bullets covering Problem, Method, Results, Limitations."
                    else:
                        instruction = "Give a detailed structured summary with: 1. Title & Authors 2. TL;DR 3. Problem Statement 4. Methodology 5. Key Findings - Top 5 6. Limitations 7. Keywords 8. Future Scope"
                    prompt = f"You are an expert research assistant. Summarize the following research paper in English.\n\n{instruction}\n\nPaper Text:\n{paper_text}"
                    summary_text = call_gemini(api_key, selected_model_id, prompt)
                    st.divider()
                    st.subheader(f"📋 Summary - {uploaded_file.name}")
                    st.markdown(summary_text)
                    st.download_button("⬇️ Download Summary as .txt", data=summary_text, file_name="summary.txt", mime="text/plain")
                    st.success("Summary Generated Successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.info("👆 Upload a PDF to get started.")