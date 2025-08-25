# toolsets/nmap_toolset.py
from typing import Dict, Any, List
import re
import nmap
from pydantic_ai.toolsets import FunctionToolset

# simple CVE extractor for any script output we see
_CVE_RE = re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE)


def nmap_scan(
    target: str,
    args: str = "-sV --script vulners,vuln --top-ports 1000"
) -> Dict[str, Any]:
    """
    Run nmap via python-nmap and return a structured dict of findings.
    Extracts CVEs from script outputs when present.

    target: single host, CIDR, or space-separated list supported by nmap
    args:   extra nmap flags (default: service detection + vuln scripts)
    """
    nm = nmap.PortScanner()
    # python-nmap wraps the nmap CLI, but no subprocess shell juggling needed
    nm.scan(hosts=target, arguments=args)

    findings: List[Dict[str, Any]] = []

    for host in nm.all_hosts():
        host_state = nm[host].state() if 'status' in nm[host] else nm[host].get('state', 'unknown')

        for proto in nm[host].all_protocols():
            ports = nm[host][proto].keys()
            for port in sorted(ports):
                pdata = nm[host][proto][port]

                # basic service info
                service = pdata.get("name", "")
                product = pdata.get("product", "")
                version = pdata.get("version", "")
                extrainfo = pdata.get("extrainfo", "")
                cpes = pdata.get("cpe", "")  # may be string or list depending on nmap version

                # script results (if any)
                script_res = pdata.get("script", {}) or {}
                # script_res is a dict: {script_name: output_str}
                cves = set()
                for out in script_res.values():
                    if not out:
                        continue
                    for m in _CVE_RE.findall(str(out)):
                        cves.add(m.upper())

                findings.append({
                    "host": host,
                    "host_state": host_state,
                    "protocol": proto,
                    "port": int(port),
                    "service": service,
                    "product": product,
                    "version": version,
                    "extrainfo": extrainfo,
                    "cpes": cpes,
                    "scripts": script_res,   # keep raw for later reasoning
                    "cves": sorted(cves),
                })

    return {
        "target": target,
        "args": args,
        "hosts": nm.all_hosts(),
        "findings": findings,
    }


def nmap_tools() -> FunctionToolset:
    # expose nmap_scan as a tool to your Agent
    return FunctionToolset(tools=[nmap_scan])