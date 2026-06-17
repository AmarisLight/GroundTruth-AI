def get_analysis_prompt(property_description: str) -> str:
    return f"""
You are a UK commercial property compliance analyst.

Analyse the following property listing description and return:
1. A financial viability score out of 100
2. The UK planning use class (e.g. E, C2, Sui Generis)
3. Top 3 compliance risks
4. A one-line investment verdict

Property Description:
{property_description}

Respond in clear sections with headers.
"""