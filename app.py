import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
from prompts import get_analysis_prompt

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(
    page_title="GroundTruth AI",
    page_icon="🏢",
    layout="centered"
)

st.title("🏢 GroundTruth AI")
st.subheader("Commercial Property Compliance & Viability Scorer")

st.markdown(
    "Enter a UK commercial property description to receive an AI-generated "
    "compliance assessment, planning use class classification, and financial "
    "viability score. Powered by GPT-4o."
)

market = st.selectbox(
    "Select Market",
    options=["UK", "Canada"],
    index=0
)

property_input = st.text_area(
    label="Property Description",
    placeholder=(
        "e.g. A 2,500 sq ft ground floor commercial unit in Manchester city "
        "centre, currently used as a restaurant (Class E). Freehold. Listed "
        "building. Adjacent to a residential development..."
    ),
    height=200
)

if st.button("🔍 Analyse Property"):

    if not property_input.strip():
        st.warning("Please paste a property description first.")

    else:
        with st.spinner("Analysing property..."):

            prompt = get_analysis_prompt(property_input, market)

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a commercial property compliance expert specialising in {market} real estate."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            result = response.choices[0].message.content

            st.session_state["result"] = result


if "result" in st.session_state:

    result = st.session_state["result"]

    # Extract and display summary card
    if "## SUMMARY" in result:

        st.divider()

        if market == "UK":
            st.info(
                "🇬🇧 Analysis performed under **UK planning regulations** — "
                "NPPF, Use Classes Order, Building Regulations 2010"
            )
        else:
            st.info(
                "🇨🇦 Analysis performed under **Canadian building codes** — "
                "National Building Code, Provincial Zoning, Heritage Designation Rules"
            )

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
            st.metric(
                "📍 Location",
                summary_data.get("Location", "N/A")
            )

            st.metric(
                "🏢 Type",
                summary_data.get("Property Type", "N/A")
            )

        with col2:
            st.metric(
                "📐 Size",
                summary_data.get("Size", "N/A")
            )

            st.metric(
                "📋 Use Class",
                summary_data.get("Use Class", "N/A")
            )

        with col3:
            st.metric(
                "💰 Price",
                summary_data.get("Asking Price", "N/A")
            )

            st.metric(
                "⭐ Score",
                summary_data.get("Viability Score", "N/A")
            )

    else:
        summary_data = {}

    st.divider()

    st.subheader("📊 Full Analysis")

    # Split out action checklist for special display
    if "## 5. Action Checklist" in result:

        main_analysis = result.split("## 5. Action Checklist")[0]

        checklist_section = result.split(
            "## 5. Action Checklist"
        )[1]

        st.markdown(main_analysis)

        st.divider()

        st.subheader("✅ Pre-Purchase Action Checklist")

        st.markdown(
            "*Complete these steps before proceeding with this investment:*"
        )

        for line in checklist_section.strip().split("\n"):

            if line.strip() and line.strip()[0].isdigit():

                st.checkbox(
                    line.strip(),
                    key=line.strip()[:50]
                )

    else:
        st.markdown(result)

# PDF Export
st.divider()

if st.button("📄 Download Report as PDF"):

    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(
        0,
        10,
        "GroundTruth AI - Property Compliance Report",
        ln=True
    )

    pdf.ln(5)

    # Property Summary
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(
        0,
        10,
        "Property Summary",
        ln=True
    )

    pdf.set_font("Helvetica", size=10)

    for key, value in summary_data.items():
        pdf.multi_cell(
            190,
            7,
            f"{key}: {value}"
        )

    pdf.ln(5)

    # Full Analysis
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(
        0,
        10,
        "Full Analysis",
        ln=True
    )

    pdf.ln(2)

    # Remove the SUMMARY section from the AI output
    analysis_text = result

    if "## SUMMARY" in analysis_text:

        parts = analysis_text.split("## SUMMARY", 1)

        if len(parts) == 2:

            after_summary = parts[1]

            # Remove everything until the next heading
            if "## " in after_summary:

                analysis_text = after_summary.split(
                    "## ",
                    1
                )[1]

                analysis_text = "## " + analysis_text

            else:
                analysis_text = ""

    # Remove duplicate action checklist from PDF if needed
    # because it is already displayed separately in the app
    if "## 5. Action Checklist" in analysis_text:

        analysis_text = analysis_text.split(
            "## 5. Action Checklist",
            1
        )[0]

    # Clean markdown
    analysis_text = analysis_text.replace("**", "")
    analysis_text = analysis_text.replace("### ", "")
    analysis_text = analysis_text.replace("## ", "")
    analysis_text = analysis_text.replace("£", "GBP ")

    # Remove markdown bullets
    analysis_text = analysis_text.replace("- ", "• ")

    # Handle Unicode safely for FPDF
    analysis_text = analysis_text.encode(
        "latin-1",
        errors="replace"
    ).decode("latin-1")

    pdf.set_font("Helvetica", size=10)

    for line in analysis_text.split("\n"):

        line = line.strip()

        if not line:
            pdf.ln(3)
            continue

        try:
            pdf.multi_cell(
                190,
                6,
                line
            )
        except Exception:
            pass

    pdf_bytes = pdf.output()

    st.download_button(
        label="📥 Click here to download your PDF report",
        data=bytes(pdf_bytes),
        file_name="groundtruth-ai-report.pdf",
        mime="application/pdf"
    )
