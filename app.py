import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
from prompts import get_analysis_prompt
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
st.set_page_config(page_title="GroundTruth AI", page_icon="🏢", layout="centered")

st.title("🏢 GroundTruth AI")
st.subheader("UK Commercial Property Compliance & Viability Scorer")
st.markdown("Enter a UK commercial property description to receive an AI-generated compliance assessment, planning use class classification, and financial viability score. Powered by GPT-4o.")

property_input = st.text_area(
    label="Property Description",
    placeholder="e.g. A 2,500 sq ft ground floor commercial unit in Manchester city centre, currently used as a restaurant (Class E). Freehold. Listed building. Adjacent to a residential development...",
    height=200
)
if st.button("🔍 Analyse Property"):
    if not property_input.strip():
        st.warning("Please paste a property description first.")
    else:
        with st.spinner("Analysing property..."):
            prompt = get_analysis_prompt(property_input)
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a UK commercial property compliance expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = response.choices[0].message.content
            st.session_state["result"] = result

if "result" in st.session_state:
    result = st.session_state["result"]
    
    # Extract and display summary card
    if "## SUMMARY" in result:
        st.divider()
        st.subheader("📋 Property Summary")
        
        lines = result.split("\n")
        summary_data = {}
        in_summary = False
        
        for line in lines:
            if "## SUMMARY" in line:
                in_summary = True
                continue
            if line.startswith("## ") and in_summary:
                break
            if in_summary and line.startswith("- "):
                parts = line[2:].split(": ", 1)
                if len(parts) == 2:
                    summary_data[parts[0].strip()] = parts[1].strip()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📍 Location", summary_data.get("Location", "N/A"))
            st.metric("🏢 Type", summary_data.get("Property Type", "N/A"))
        with col2:
            st.metric("📐 Size", summary_data.get("Size", "N/A"))
            st.metric("📋 Use Class", summary_data.get("Use Class", "N/A"))
        with col3:
            st.metric("💰 Price", summary_data.get("Asking Price", "N/A"))
            st.metric("⭐ Score", summary_data.get("Viability Score", "N/A"))
    
    st.divider()
    st.subheader("📊 Full Analysis")
    
    # Split out action checklist for special display
    if "## 5. Action Checklist" in result:
        main_analysis = result.split("## 5. Action Checklist")[0]
        checklist_section = result.split("## 5. Action Checklist")[1]
        
        st.markdown(main_analysis)
        
        st.divider()
        st.subheader("✅ Pre-Purchase Action Checklist")
        st.markdown("*Complete these steps before proceeding with this investment:*")
        
        for line in checklist_section.strip().split("\n"):
            if line.strip() and line.strip()[0].isdigit():
                st.checkbox(line.strip(), key=line.strip()[:50])
        
    else:
        st.markdown(result)

    # PDF Export
    st.divider()
    if st.button("📄 Download Report as PDF"):
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "GroundTruth AI - Property Compliance Report", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Property Summary", ln=True)
        pdf.set_font("Helvetica", size=11)
        for key, value in summary_data.items():
            pdf.cell(0, 8, f"{key}: {value}", ln=True)
        
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Full Analysis", ln=True)
        pdf.set_font("Helvetica", size=10)
        
        clean_result = result.replace("##", "").replace("**", "")
        for line in clean_result.split("\n"):
            if line.strip():
                try:
                    pdf.multi_cell(0, 7, line.strip())
                except Exception:
                    pass
        
        pdf_bytes = pdf.output()
        st.download_button(
            label="📥 Click here to download your PDF report",
            data=bytes(pdf_bytes),
            file_name="groundtruth-ai-report.pdf",
            mime="application/pdf"
        )