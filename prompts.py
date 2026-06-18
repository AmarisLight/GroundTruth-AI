def get_analysis_prompt(property_description: str) -> str:
    return f"""
You are a UK commercial property compliance analyst.

Analyse the following property listing description and return your response in exactly this structure:

## SUMMARY
- Location: [extract or state Unknown]
- Property Type: [extract or state Unknown]
- Size: [extract or state Unknown]
- Use Class: [e.g. Class E, C2, Sui Generis, or Unknown]
- Asking Price: [extract or state Unknown]
- Viability Score: [score out of 100]

## 1. Financial Viability Score
[Score and explanation]

## 2. UK Planning Use Class
[Use class and explanation]

## 3. Top 3 Compliance Risks
[Numbered list of risks]

## 4. Investment Verdict
[One line verdict]

## 5. Action Checklist
Provide a numbered list of 5 specific actions the investor must take before proceeding. Be specific and practical. Each action should directly address a compliance risk or due diligence gap identified above.

Property Description:
{property_description}
"""