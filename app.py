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
st.markdown("Paste a UK commercial property listing below and get an instant compliance analysis and financial viability score.")
st.divider()

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
    st.divider()
    st.subheader("📊 Analysis Result")
    st.markdown(st.session_state["result"])