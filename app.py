import streamlit as st
from pptx import Presentation

def count_slides(file):
    prs = Presentation(file)
    return len(prs.slides)

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
        slide_count = count_slides(uploaded_file)
        if not (5 <= slide_count <= 20):
            st.error(f"Invalid slide count: {slide_count}. Must be between 5 and 20.")
        else:
            st.success(f"Valid file with {slide_count} slides.")
            if st.button("Proceed to Analysis"):
                st.session_state["pptx_file"] = uploaded_file
                st.session_state["slide_count"] = slide_count
                st.success("Ready to extract text.")

