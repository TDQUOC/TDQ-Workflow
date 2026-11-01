"""Assemble request documentation from existing evidence; never executes tests."""
from pathlib import Path
import hashlib
import html
import json

ROOT = Path(__file__).resolve().parents[4]
E = Path(__file__).resolve().parent
SLUG = E.name
def bind(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

index = json.loads((E / "evidence-index.json").read_text(encoding="utf-8"))
q5 = index["checks"]["Q5"]
q5["receipt"] = bind(E / "runs/final-offline-export-ed7b52e79d6c40d4859e87c4e2cfb4d0/receipt.json")
for role, suffix in (("json", "json"), ("markdown", "md"), ("html", "html")):
    q5[role] = bind(E / ("slow-tests." + suffix))
write_json(E / "evidence-index.json", index)

result = json.loads((E / "final-result.json").read_text(encoding="utf-8"))
runtime = json.loads((E / "runtime.json").read_text(encoding="utf-8"))
source = runtime["source_sha256"]
input_sha = bind(E / "final-result.json")["sha256"]
timing = (E / "timing-final.txt").read_text(encoding="utf-8-sig")
sections = [
    ("results", "Kết quả", "Đã triển khai bốn hạng mục: validation calibration sớm; timeout và ownership tiến trình Codex; giảm công việc lặp trong kiểm thuần; Top20 case/module cùng export offline JSON/MD/HTML. Full: 3657 PASS, 8 SKIP, 3665 case; giữ đủ 3602 case baseline và thêm 63 case. Wall 1030.256894399994 giây; tổng execution phases 1018.7496596999772 giây, hai đại lượng được tách riêng."),
    ("before-after", "Thay đổi đã đo", "11 ca kiểm thuần có 0 lời gọi subprocess/calibration/Git sau chuyển đổi; mapping giữ 43 assertion anchors. Bốn integration thực vẫn có 403/3/39/18 lời gọi subprocess được observer Python ghi nhận. Đây là audit Python, không phải đếm mọi lần OS tạo tiến trình; không suy ra phần trăm tăng tốc Full."),
    ("raw-samples", "Runtime và nguồn số liệu", "Bốn scenario thực: calibration-valid 11.3050513s; reject-early 0.3452787s, không đo và không tạo output; timeout-cleanup 2.7218578s với timeout 2s, descendants hết và HOME được dọn; report-offline 1.2800396s, không gọi runner. Mỗi scenario có cap 120s; timeout có ngưỡng 8s gồm cleanup. Calibration dùng private true.cmd fixture trên Windows; không phải kiểm mô hình từ xa."),
    ("limitations", "Giới hạn và trạng thái", "Benchmark A/B D9/D10 giữ SKIPPED_USER; chưa chứng nhận phần trăm hiệu năng, POSIX hay thiết bị vật lý. Giữ worker1/cacheoff. Các receipt FAIL trung gian vẫn được bảo toàn, chỉ receipt cuối đúng source được dùng chứng nhận. Guard chỉ bỏ qua giá trị usageCount/lastUsedAt đã duyệt; cấu trúc/type/presence và cấu hình khác vẫn được bảo vệ. Metadata workflow còn phase=implement do 11 worktree cũ dirty; không xóa dữ liệu hoặc bypass guard. Chưa commit/push; nhánh codex/toi-uu-bon-hang-muc."),
    ("recommendations", "Đề xuất tiếp theo", "Dùng Top20 từ mỗi result để chọn vùng tối ưu tiếp; tiếp tục ưu tiên loại bỏ công việc lặp ở kiểm thuần và giữ integration thật. Chưa bật worker/cache mặc định khi chưa có A/B phù hợp. Review độc lập, kết quả Q1–Q8 và browser được lưu riêng, liên kết bên dưới; metadata blocker không được trình bày thành workflow đã đóng."),
    ("rollback", "Vận hành và rollback", "Đọc report offline bằng python scripts/tdq_test.py report --result <result.json> --out-prefix <prefix>. Kiểm bảo thủ dùng python scripts/tdq_test.py tron-bo --workers 1 --fresh --reuse off. Chưa tạo commit triển khai mới nên chưa có commit rollback; preimages theo task trong integration-backup/, chỉ hoàn nguyên đúng file thuộc request sau khi đối chiếu diff, giữ dữ liệu người dùng."),
]
links = [("slow-tests.html", "Top20 HTML"), ("slow-tests.md", "Top20 Markdown"), ("final-result.json", "Raw Full result"), ("QC-F1-check.json", "Full kiểm chứng"), ("runtime.json", "Runtime evidence"), ("final-work-proof.json", "Work counters"), ("case-mapping.json", "Case/assertion mapping"), ("phase-transition-blocker.json", "Workflow blocker"), ("telemetry-exception-approved.md", "Ngoại lệ đã duyệt"), ("independent-qc.md", "Review độc lập")]
md = [f"# REPORT — Tối ưu bốn hạng mục ({SLUG})", "", "Soul: chất lượng > runtime > context cost · lane full · mode subagent", "", f"Source SHA256: {source}", f"Input SHA256: {input_sha}", ""]
for sid, title, body in sections:
    md += [f"<!-- {sid} -->", f"## {title}", "", body, ""]
md += ["## Bằng chứng", ""] + [f"- [{label}]({href})" for href, label in links] + ["", "## Thời gian", "", "Bảng dưới được chép nguyên output tdq_timing.py show; các giá trị partial/unavailable không được suy đoán.", "", timing]
(E / "request-report.md").write_text("\n".join(md), encoding="utf-8")
css = "body{font:16px/1.6 system-ui,sans-serif;margin:0;color:#182238;background:#f4f6fb}main{max-width:960px;margin:auto;padding:24px}header,section{background:white;border:1px solid #dce3ef;border-radius:12px;padding:22px;margin-bottom:18px}h1{font-size:30px;line-height:1.2}h2{font-size:22px}a{color:#154dc4}nav{display:flex;gap:12px;flex-wrap:wrap}p,li,code,pre{overflow-wrap:anywhere}pre{white-space:pre-wrap;font-size:12px}a:focus{outline:3px solid #995c00;outline-offset:3px}@media(max-width:480px){main{padding:12px}header,section{padding:16px}h1{font-size:25px}}"
parts = [f'<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Báo cáo tối ưu bốn hạng mục</title><style>{css}</style><main><header><h1>Tối ưu bốn hạng mục</h1><p>{html.escape(SLUG)} · lane full · subagent</p><p>Source SHA256: {source}</p><p>Input SHA256: {input_sha}</p><nav aria-label="Mục báo cáo">']
parts += [f'<a href="#{sid}">{html.escape(title)}</a>' for sid, title, _ in sections]
parts += ['</nav></header>']
for sid, title, body in sections:
    parts += [f'<section id="{sid}"><h2>{html.escape(title)}</h2><p>{html.escape(body)}</p></section>']
parts += ['<section id="evidence"><h2>Bằng chứng</h2><ul>'] + [f'<li><a href="{href}">{html.escape(label)}</a></li>' for href, label in links] + ['</ul></section>', '<section id="timing"><h2>Thời gian</h2><p>Output tdq_timing.py show; partial/unavailable không được suy đoán.</p><pre>' + html.escape(timing) + '</pre></section></main></html>']
(E / "request-report.html").write_text("\n".join(parts), encoding="utf-8")
report_path = ROOT / "docs/tdq/reports" / (SLUG + ".md")
report_path.parent.mkdir(exist_ok=True)
public = "\n".join(md).replace("](slow-tests", f"](../artifacts/{SLUG}/slow-tests")
# Keep one canonical evidence folder; public entry links to both final artifacts.
report_path.write_text(f"# REPORT — Tối ưu bốn hạng mục\n\nĐã triển khai đủ bốn hạng mục. Full: **3657 PASS, 8 SKIP**; giữ đủ 3602 case baseline. Chưa commit/push.\n\n[Báo cáo đầy đủ](../artifacts/{SLUG}/request-report.md) · [HTML](../artifacts/{SLUG}/request-report.html) · [Top20](../artifacts/{SLUG}/slow-tests.html)\n\nGiới hạn: D9/D10 SKIPPED_USER; không chứng nhận % tăng tốc. Metadata phase=implement còn bị chặn bởi 11 worktree cũ dirty.\n\n## Thời gian\n\n{timing}", encoding="utf-8")
print(json.dumps({"report": bind(E / "request-report.html"), "index": bind(E / "evidence-index.json")}, ensure_ascii=False))
