import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
from markdown_it import MarkdownIt

A = Path(__file__).resolve().parent
ROOT = A.parents[3]
slug = A.name
report = ROOT / "docs" / "tdq" / "reports" / (slug + "-test-review.md")
output = report.with_suffix(".html")
source = report.read_text(encoding="utf-8")
body = MarkdownIt("commonmark").enable("table").render(source)
body = body.replace("<table>", '<div class="table-scroll"><table>').replace("</table>", "</table></div>")
html = '''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>TDQ — Kiểm chứng test và đề xuất tối ưu</title>
<style>
:root{color-scheme:light;--ink:#19362f;--muted:#52655e;--line:#d6dfd7}*{box-sizing:border-box}body{margin:0;background:#f5f4ef;color:var(--ink);font:16px/1.7 system-ui,"Segoe UI",sans-serif}header,main,footer{max-width:1160px;margin:auto;padding:24px 32px}header{font-size:12px;letter-spacing:.1em;border-bottom:1px solid var(--line);color:#176953}main{padding-bottom:60px}h1{font-size:clamp(30px,5vw,48px);line-height:1.15;letter-spacing:-.035em;max-width:920px}h2{font-size:26px;line-height:1.3;margin:46px 0 18px;border-top:1px solid var(--line);padding-top:28px}h3{font-size:20px;margin-top:30px}p,li{max-width:1000px}li{margin:10px 0}a{color:#0b6d58;text-underline-offset:3px;overflow-wrap:anywhere}code{font: .88em Consolas,monospace;background:#e9ede6;border-radius:4px;padding:2px 5px;overflow-wrap:anywhere}strong{font-weight:700}.table-scroll{overflow-x:auto;border:1px solid var(--line);border-radius:12px;margin:22px 0;background:white}table{border-collapse:collapse;width:100%;min-width:700px;font-size:14px}th,td{padding:14px 16px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}th{background:#e4eee6}tr:last-child td{border:0}footer{font-size:13px;color:var(--muted);border-top:1px solid var(--line)}@media(max-width:650px){header,main,footer{padding-left:18px;padding-right:18px}body{font-size:15px}h2{font-size:23px}table{min-width:800px}}@media print{body{background:white;font-size:10pt}header,main,footer{max-width:none;padding:0}h1{font-size:25pt}h2{font-size:17pt;break-after:avoid}.table-scroll{overflow:visible;border:0}table{min-width:0;font-size:8pt}th,td{padding:7px}a{color:inherit}}
</style></head><body><header>TDQ / WORKFLOW ENGINEERING · REVIEW BỔ SUNG · 27.10.2026</header><main>'''
html += body + '</main><footer>Bản bổ sung cho báo cáo đợt 1. Giữ đầy đủ kết quả ERROR/FAIL và các giới hạn bằng chứng.</footer></body></html>'
output.write_text(html, encoding="utf-8")

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.texts = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.append(dict(attrs).get("href", ""))
    def handle_data(self, data):
        self.texts.append(data)

parser = Links()
parser.feed(html)
missing = [href for href in parser.links if not urlsplit(href).scheme
           and not (output.parent / unquote(urlsplit(href).path)).exists()]
text = " ".join(parser.texts)
checks = {"all_local_links_exist": not missing, "no_external_assets": '<script' not in html and '<link' not in html and '<img' not in html,
          "critical_results_present": all(value in text for value in ("3.306", "13 skip", "1 ERROR", "1 FAIL", "342", "688,269")),
          "full_rendered_markdown_included": body in html, "responsive_table_wrappers": body.count('<table>') == body.count('class="table-scroll"')}
proof = {"checks": checks, "missing_links": missing, "links": len(parser.links),
         "markdown_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
         "html_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
         "validation_scope": "Static structure/content/link checks; no fresh browser screenshot for this supplemental report"}
(A / "review-html-proof.json").write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
print(json.dumps(proof, indent=2))
raise SystemExit(0 if all(checks.values()) else 1)
