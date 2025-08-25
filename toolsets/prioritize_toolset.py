# toolsets/prioritize_toolset.py
from pydantic_ai.toolsets import FunctionToolset

KEYWORDS = ("remote code execution", "rce", "auth bypass", "privilege escalation", "pre-auth")

def prioritize(findings: list[dict], enriched: list[dict]) -> dict:
    sev_map = {e["id"]: ("high" if (e.get("cvss3") or e.get("cvss") or 0) >= 7.0
                         or any(k in (e.get("summary","").lower()) for k in KEYWORDS)
                         else "medium")
               for e in enriched if "id" in e}
    flagged = []
    for f in findings:
        tags = [sev_map.get(cid, "info") for cid in f.get("cves", [])]
        worst = "info"
        if "high" in tags: worst = "high"
        elif "medium" in tags: worst = "medium"
        flagged.append({**f, "severity": worst})
    return {"flagged": flagged}

def prioritize_tools():
    return FunctionToolset(tools=[prioritize])