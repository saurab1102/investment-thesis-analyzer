import streamlit as st
from pptx import Presentation

def count_slides(file):
    prs = Presentation(file)
    return len(prs.slides)

def extract_slide_text(file):
    prs = Presentation(file)
    slide_texts = []
    for i, slide in enumerate(prs.slides):
        content = []
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text = shape.text.strip()
                if text:
                    content.append(text)
        slide_texts.append({"slide_num": i + 1, "text": " ".join(content)})
    return slide_texts


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
                with st.spinner("Extracting text from slides..."):
                     slide_data = extract_slide_text(uploaded_file)
                     st.session_state["slide_data"] = slide_data
                     st.success("Text extraction complete.")
                     #st.subheader("Extracted Slide Text")
                     #for slide in slide_data:
                     #    st.markdown(f"**Slide {slide['slide_num']}**")
                     #    st.write(slide['text'])
                     total_text = sum(len(s["text"]) for s in slide_data)
                     if total_text == 0:
                         st.error("No readable text found in the deck.")

