import streamlit as st
from pptx import Presentation
from llm_client import query_together
import json
import re
from report_generator import generate_pdf_report

REQUIRED_TYPES = [
    "Problem", "Solution", "Market", "Business Model",
    "Competition", "Team", "Financials", "Traction", "Funding Ask"
]

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

def build_classification_prompt(slides):
    intro = (
        "You are an AI assistant that classifies slides from a startup pitch deck. "
        "Each slide must be assigned one of the following categories:\n"
        "Problem, Solution, Market, Business Model, Competition, Team, Financials, Traction, Funding Ask, Unclassified.\n"
        "For each slide, respond in this JSON format:\n"
        "{\"slide_num\": 1, \"category\": \"Team\"}\n"
        "Here are the slides:\n"
    )
    body = ""
    for slide in slides:
        body += f"\nSlide {slide['slide_num']}:\n{slide['text']}\n"
    return intro + body

def classify_slides_with_llm(slides):
    prompt = build_classification_prompt(slides)
    raw_output = query_together(prompt)
    return raw_output

def parse_classification_output(output_text):
    try:
        return json.loads(output_text)
    except json.JSONDecodeError as e:
        raise ValueError("LLM returned invalid JSON") from e

def classify_single_slide(text):
    prompt = (
        "Classify the following slide into one of the categories:\n"
        "Problem, Solution, Market, Business Model, Competition, Team, Financials, Traction, Funding Ask, Unclassified.\n\n"
        f"Slide Content:\n\"{text}\"\n\n"
        "Return only the category as a single word."
    )
    return query_together(prompt)

def classify_all_slides(slides):
    results = []
    for slide in slides:
        try:
            label = classify_single_slide(slide["text"])
            slide["category"] = label.strip()
        except Exception:
            slide["category"] = "Unclassified"
        results.append(slide)
    return results
    
    
def build_analysis_prompt(slides):
    classified = [s for s in slides if s.get("category") != "Unclassified"]

    header = (
        "You are an AI investment analyst. Based on the following pitch deck content, produce an investment thesis. "
        "Return your response as a JSON object with the following fields:\n\n"
        "- recommendation: one of [\"Strong Buy\", \"Hold\", \"Pass\"]\n"
        "- overall_score: integer 0–100\n"
        "- processing_date: use current UTC in format DD-MM-YYYY HH:MM:SS UTC\n"
        "- confidence_score: integer 0–100\n"
        "- strengths: list of 3–5 strings\n"
        "- weaknesses: list of 3–5 strings\n"
        "- recommendations: string (100–200 words)\n"
        "- categories: list of 9 objects, each with:\n"
        "  - name (category name),\n"
        "  - score (0–10),\n"
        "  - weight (int %),\n"
        "  - feedback (50–150 words)\n\n"
        "Use these fixed weights: Problem 10, Solution 15, Market 20, Business Model 15, Competition 10, Team 15, "
        "Traction 10, Financials 10, Clarity 5\n\n"
        "Classified Slides:\n"
    )

    grouped = {}
    for slide in classified:
        cat = slide["category"]
        grouped.setdefault(cat, []).append(slide["text"])

    body = ""
    for cat in grouped:
        content = "\n".join(grouped[cat])
        body += f"\n---\nCategory: {cat}\n{content}\n"

    return header + body

def analyze_pitch(slides):
    prompt = build_analysis_prompt(slides)
    raw_output = query_together(prompt, max_tokens=3000)
    return raw_output

def parse_analysis_output(raw_text):
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```json\s*|```$", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^```\s*|```$", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^---\s*", "", cleaned)
    print(cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError("Invalid JSON in LLM analysis output.") from e



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

            if "slide_data" not in st.session_state:
                if st.button("Proceed to Analysis"):
                    with st.spinner("Extracting text from slides..."):
                        slide_data = extract_slide_text(uploaded_file)
                        st.session_state["slide_data"] = slide_data
                        st.success("Text extraction complete.")

if "slide_data" in st.session_state:
    slide_data = st.session_state["slide_data"]

    if st.button("Classify Slides with AI"):
        with st.spinner("Classifying each slide..."):
            classified_slides = classify_all_slides(slide_data)
            print([s["category"] for s in classified_slides])
            st.session_state["classified_slides"] = classified_slides

            found_types = {s["category"] for s in classified_slides if s["category"] in REQUIRED_TYPES}
            if len(found_types) < 3:
                st.error(f"Only {len(found_types)} valid categories found: {', '.join(found_types)}")
            else:
                st.success(f"Classification complete. Categories found: {', '.join(found_types)}")

if "classified_slides" in st.session_state:
    if st.button("Run Investment Analysis"):
        with st.spinner("Analyzing pitch deck..."):
            try:
                raw_analysis = analyze_pitch(st.session_state["classified_slides"])
                parsed = parse_analysis_output(raw_analysis)
                st.session_state["analysis_result"] = parsed
                st.success("Analysis complete.")
            except Exception as e:
                st.error(str(e))
                st.stop()

        # Optional debug: display result
        st.subheader("Investment Recommendation")
        st.write(parsed["recommendation"])
        st.write(f"Overall Score: {parsed['overall_score']}")
        st.write(f"Confidence Score: {parsed['confidence_score']}")
        
if "analysis_result" in st.session_state:
    if st.button("Generate PDF Report"):
        pdf_bytes, pdf_name = generate_pdf_report(st.session_state["analysis_result"], startup_name="DemoStartup")
        st.download_button(label="Download Report", data=pdf_bytes, file_name=pdf_name, mime="application/pdf")



