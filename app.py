import streamlit as st

st.set_page_config(page_title="Investment Thesis Generator", layout="centered")

st.title("Automated Investment Thesis Generator (POC)")

st.markdown("""
Upload a startup pitch deck in .pptx format. The deck should have 5–20 slides and include at least 3 of the following:  
- Problem  
- Solution/Product  
- Market  
- Business Model  
- Competition  
- Team  
- Financials  
- Traction  
- Funding Ask
""")

uploaded_file = st.file_uploader("Upload your PowerPoint (.pptx only)", type=["pptx"])

if uploaded_file:
    if uploaded_file.size > 50 * 1024 * 1024:
        st.error("File size exceeds 50MB.")
    else:
        st.success("File uploaded successfully.")

