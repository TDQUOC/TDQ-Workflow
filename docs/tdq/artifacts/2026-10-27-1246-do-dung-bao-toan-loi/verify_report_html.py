from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit
from markdown_it import MarkdownIt

class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = []
        self.text = []
        self.article_text = []
        self.in_article = False
        self.assets = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "article":
            self.in_article = True
        if tag == "a" and "href" in values:
            self.links.append(values["href"])
        if "id" in values:
            self.ids.append(values["id"])
        if "src" in values or (tag == "link" and values.get("rel") == "stylesheet"):
            self.assets.append(values.get("src", values.get("href")))

    def handle_endtag(self, tag):
        if tag == "article":
            self.in_article = False

    def handle_data(self, data):
        self.text.append(data)
        if self.in_article:
            self.article_text.append(data)

artifact_dir = Path(__file__).resolve().parent
root = artifact_dir.parents[3]
receipt = json.loads((artifact_dir / "report-html-build.json").read_text(encoding="utf-8"))
source = root / receipt["source"]
target = root / receipt["html"]
actual = Document()
actual.feed(target.read_text(encoding="utf-8"))
expected = Document()
expected.feed(MarkdownIt("commonmark", {"html": False}).enable("table").render(source.read_text(encoding="utf-8")))
broken = []
for href in actual.links:
    parsed = urlsplit(href)
    if parsed.scheme:
        continue
    if not parsed.path:
        if parsed.fragment not in actual.ids:
            broken.append(href)
    elif not (target.parent / unquote(parsed.path)).resolve().is_file():
        broken.append(href)
checks = {
    "source_hash_preserved": sha256(source.read_bytes()).hexdigest() == receipt["source_sha256"],
    "html_hash_matches": sha256(target.read_bytes()).hexdigest() == receipt["html_sha256"],
    "full_report_text_preserved": " ".join("".join(actual.article_text).split()) == " ".join("".join(expected.text).split()),
    "all_links_resolve": not broken,
    "unique_anchor_ids": len(actual.ids) == len(set(actual.ids)),
    "no_external_assets": not actual.assets,
}
result = {"checks": checks, "link_count": len(actual.links), "broken_links": broken,
          "source_sha256": receipt["source_sha256"], "html_sha256": receipt["html_sha256"]}
(artifact_dir / "report-html-content-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
sys.exit(0 if all(checks.values()) else 1)
