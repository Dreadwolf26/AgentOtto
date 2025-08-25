# toolsets/cve_toolset.py
import requests, time
from pydantic_ai.toolsets import FunctionToolset

CIRCL = "https://cve.circl.lu/api/cve/{}"

def cve_enrich(cves: list[str]) -> list[dict]:
    """
    For each CVE ID, return {id, summary, cvss, cvss3, published, references}.
    Slow but simple; add caching later.
    """
    out = []
    for cid in cves:
        try:
            r = requests.get(CIRCL.format(cid), timeout=10)
            if r.status_code == 200:
                d = r.json()
                out.append({
                    "id": cid,
                    "summary": d.get("summary"),
                    "cvss": d.get("cvss"),
                    "cvss3": d.get("cvss3"),
                    "published": d.get("Published"),
                    "references": d.get("references", []),
                })
            else:
                out.append({"id": cid, "error": f"HTTP {r.status_code}"})
        except Exception as e:
            out.append({"id": cid, "error": str(e)})
        time.sleep(0.2)  # be polite
    return out

def cve_tools():
    return FunctionToolset(tools=[cve_enrich])