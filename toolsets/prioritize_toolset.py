# toolsets/prioritize_toolset.py
from pydantic_ai.toolsets import FunctionToolset

KEYWORDS = ("remote code execution", "rce", "auth bypass",
            "privilege escalation", "pre-auth")


def prioritize(findings: list[dict], enriched: list[dict]) -> dict:
    sev_map = {}
    for e in enriched:
        cid = e.get("id")
        if not cid:
            continue

        # safe defaults
        cvss_val = e.get("cvss3") or e.get("cvss") or 0
        summary = e.get("summary") or ""   # <- fix here
        summary_lower = summary.lower()

        high_flag = (cvss_val >= 7.0) or any(k in summary_lower for k in KEYWORDS)

        sev_map[cid] = "high" if high_flag else "medium"

    flagged = []
    for f in findings:
        tags = [sev_map.get(cid, "info") for cid in f.get("cves", [])]
        worst = "info"
        if "high" in tags:
            worst = "high"
        elif "medium" in tags:
            worst = "medium"
        flagged.append({**f, "severity": worst})

    return {"flagged": flagged}


def prioritize_tools():
    return FunctionToolset(tools=[prioritize])