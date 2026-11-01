"""Render a local progress report from preserved task receipts; never certify DoD."""
import html
import hashlib
import json
from collections import Counter
from pathlib import Path
import re
from datetime import datetime

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SLUG = OUT.name


def esc(value):
    return html.escape(str(value))


def href(path):
    return '../../../../' + Path(path).as_posix()


def latest(task):
    folder = ROOT / '.tdq-worktrees' / SLUG / task.lower() / 'docs/tdq/artifacts' / SLUG / 'runs'
    paths = [p for base in (folder, OUT / 'runs') for p in base.glob('*/receipt.json')
             if re.fullmatch(re.escape(task) + r'-[a-f0-9]{32}', p.parent.name)]
    if not paths:
        return {'task': task, 'status': 'Chưa có receipt chứng nhận mới', 'cases': '—', 'seconds': '—'}
    path = max(paths, key=lambda p: p.stat().st_mtime_ns)
    receipt = json.loads(path.read_text(encoding='utf-8'))
    stdout = (path.parent / 'stdout.txt').read_text(encoding='utf-8')
    summary = re.findall(r'[^\n]*(?:\d+ passed|\d+ failed)[^\n]*', stdout)
    if task == 'QC-F1':
        marker = next(line[11:] for line in stdout.splitlines() if line.startswith('TDQ_RESULT '))
        binding = json.loads(marker)
        result_path = Path(binding['path'])
        assert result_path.resolve().is_relative_to(ROOT)
        assert hashlib.sha256(result_path.read_bytes()).hexdigest() == binding['sha256']
        counts = Counter(case['outcome'] for case in json.loads(result_path.read_text(encoding='utf-8'))['case_outcomes'])
        summary = [f"{counts['pass']} pass / {counts['fail']} fail / {counts['skip']} skip (case chuẩn hóa, trước QC1)"]
    guard = receipt.get('verdict') == 'PASS'
    changes = [name for name, value in receipt.get('config_before', {}).items()
               if receipt.get('config_after', {}).get(name) != value]
    return {'task': task, 'status': 'Đạt gate module' if guard else 'Chưa đạt gate',
            'cases': summary[-1].strip() if summary else 'Xem stdout',
            'seconds': round(receipt['finished'] - receipt['started'], 3) if receipt.get('finished') else '—',
            'verdict': receipt.get('verdict'), 'child_exit': receipt.get('exit_code'),
            'failures': [item.get('stage') for item in receipt.get('failures', [])],
            'changed_config': changes, 'receipt': path.relative_to(ROOT).as_posix()}


def render():
    tasks = [latest(task) for task in ('T1.2', 'T2.1', 'T3.1', 'T3.2', 'T4.1', 'T4.2',
                                     'QC-F1', 'QC1.1', 'QC1.2', 'QC1.3', 'QC1.4')]
    plan = (ROOT / 'docs/tdq/plan' / (SLUG + '.md')).read_text(encoding='utf-8')
    completed = len(re.findall(r'^- \[x\] \*\*(?:T|QC)\d+\.\d+\*\*', plan, re.M))
    total = len(re.findall(r'^- \[[ x~>]\] \*\*(?:T|QC)\d+\.\d+\*\*', plan, re.M))
    now = datetime.now().astimezone().isoformat(timespec='seconds')
    data = {'request': SLUG, 'generated_at': now, 'kind': 'implementation-checkpoint',
            'final_dod_certified': False, 'full_benchmark_completed': False,
            'completed_tasks': completed, 'total_tasks': total, 'tasks': tasks}
    (OUT / 'checkpoint.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    rows = []
    for row in tasks:
        link = f'<a href="{esc(href(row["receipt"]))}">Receipt</a>' if row.get('receipt') else 'Đang chờ'
        reason = ', '.join(row.get('failures', [])) or '—'
        if row.get('changed_config'):
            reason += ': ' + ', '.join(row['changed_config'])
        rows.append(f'<tr><th>{esc(row["task"])}</th><td>{esc(row["cases"])}</td>'
                    f'<td>{esc(row["status"])}</td><td>{esc(reason)}</td><td>{link}</td></tr>')
    dod = [
        ('D1–D2', 'Inventory và tokenizer', 'Full trước QC1 có đủ 3306 case gốc và 273 case mới; chưa chứng nhận outcome toàn suite sau sửa.'),
        ('D3–D4', 'Isolation, timeout, runner và ledger', 'Gate runner module đã đạt; Full trước QC1 còn lỗi và config guard FAIL. POSIX chưa được chứng nhận trên máy Windows.'),
        ('D5–D6', 'Receipt, reuse và join', 'Module receipt đạt gate; đã có regression invalidation, lease/crash và failure provenance. Chờ xác nhận trong Full và runtime cuối.'),
        ('D7–D8', 'Readiness và transcript', 'Đã có kiểm tra off/cold/warm, mutation và lỗi đọc; chưa có số đo hiệu năng cuối trên nguồn thật.'),
        ('D9', 'Ba cặp Full A/B', 'Chưa chạy benchmark toàn suite. Không công bố phần trăm tăng tốc.'),
        ('D10', 'Ba bộ off/cold/warm cho mỗi cache', 'Harness benchmark đã kiểm bằng fixture simulation; phép đo cuối và nhóm log Claude/Codex thật chưa chạy.'),
        ('D11', 'Runtime và QC độc lập', 'Đã có review source và các lượt sửa finding kèm evidence; chưa chứng nhận QC Ultra cuối hoặc toàn bộ DoD.'),
        ('D12', 'Báo cáo và kiểm browser', 'Đây là checkpoint. Báo cáo cuối cần kết quả Full, benchmark và QC còn thiếu.')]
    dod_rows = ''.join(f'<tr><th>{esc(a)}</th><td>{esc(b)}</td><td>{esc(c)}</td></tr>' for a,b,c in dod)
    links = [
        ('Spec đã duyệt', f'docs/tdq/spec/{SLUG}.md'),
        ('Plan và task còn mở', f'docs/tdq/plan/{SLUG}.md'),
        ('Review độc lập và follow-up', f'docs/tdq/artifacts/{SLUG}/independent-pre-review.json'),
        ('Nhật ký phát hiện kỹ thuật', f'docs/tdq/artifacts/{SLUG}/build-observations.json'),
        ('Quan sát thay đổi cấu hình ngoài test', f'docs/tdq/artifacts/{SLUG}/config-churn-observation-2.json'),
        ('Đối chiếu inventory Full với 3306 case gốc', f'docs/tdq/artifacts/{SLUG}/full-collection-comparison.json'),
        ('Danh sách các lượt chạy và config guard', f'docs/tdq/artifacts/{SLUG}/run-inventory.json'),
        ('Hướng dẫn bật/tắt tối ưu', 'skills/tdq-build/references/runtime-speed.md'),
        ('Master kiến trúc — snapshot trước QC1', 'docs/architecture/index.html')]
    link_html = ''.join(f'<li><a href="{esc(href(path))}">{esc(title)}</a></li>' for title,path in links)
    document = '''<!doctype html>
<html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TDQ Runtime — Checkpoint triển khai và kiểm chứng</title>
<style>
:root{color-scheme:light;--ink:#172b3a;--muted:#516574;--line:#d7e2e8;--accent:#096b73;--bg:#f3f7f8}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 system-ui,Segoe UI,sans-serif}
main{max-width:1120px;margin:auto;padding:32px 24px 64px}header{padding:30px;border-radius:18px;background:#123842;color:#fff}
h1{font-size:clamp(28px,4vw,42px);line-height:1.2;margin:10px 0 18px}h2{font-size:25px;line-height:1.3;margin:0 0 18px}h3{font-size:19px;margin:0 0 10px}
p{margin:0 0 14px}a{color:var(--accent);text-underline-offset:3px}a:focus-visible,summary:focus-visible{outline:3px solid #d68a1a;outline-offset:4px}
a:hover{text-decoration-thickness:3px}header a{color:#c6f2ef}.eyebrow{font-size:12px;letter-spacing:1.8px;text-transform:uppercase;color:#b8dcd9}
.banner{margin-top:22px;padding:20px 24px;border-left:5px solid #c07a13;background:#fff3dc;border-radius:8px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:22px 0}
.card,section{background:white;border:1px solid var(--line);border-radius:14px;padding:24px}.card strong{display:block;font-size:27px;color:var(--accent)}.muted{color:var(--muted);font-size:14px}
section{margin-top:22px;scroll-margin-top:20px}nav{display:flex;flex-wrap:wrap;gap:10px 22px;margin:22px 0}nav a{font-weight:650}
table{width:100%;border-collapse:collapse;text-align:left;font-size:14px}th,td{padding:12px 10px;vertical-align:top;border-bottom:1px solid var(--line);overflow-wrap:anywhere}thead{background:#eef5f6}th{font-weight:700;min-width:105px}
.table-wrap{overflow-x:auto}code{background:#edf2f4;border-radius:4px;padding:2px 5px;font-size:13px;overflow-wrap:anywhere}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#edf2f4;padding:16px;border-radius:8px;font-size:13px}
li{margin:8px 0}details{border:1px solid var(--line);border-radius:8px;padding:14px 18px;margin:14px 0}summary{cursor:pointer;font-weight:700}.tag{display:inline-block;padding:3px 9px;background:#e6f1ef;color:#20554c;border-radius:6px;font-size:12px;font-weight:700}
footer{margin-top:25px;color:var(--muted);font-size:13px}@media(max-width:600px){main{padding:16px 12px 40px}header,section,.card{padding:20px}.grid{grid-template-columns:1fr;gap:10px}.card strong{font-size:24px}table{min-width:620px}nav{gap:8px 16px}h2{font-size:22px}}
@media print{body{background:white}main{max-width:none;padding:0}header{color:#172b3a;background:#edf2f4}section,.card{break-inside:avoid}nav{display:none}}
</style><main>
<header><div class="eyebrow">TDQ Workflow / Checkpoint triển khai</div>
<h1>Đã triển khai và sửa vòng QC đầu.<br>Full chưa đạt; chưa chốt tốc độ.</h1>
<p>Bản này giúp bạn xem rõ đã làm gì, phần nào đã kiểm, điểm đang chặn và điều kiện để hoàn tất request.</p>
<p class="eyebrow">__SLUG__ · cập nhật __TIME__</p></header>
<div class="banner"><strong>Chưa đóng request, chưa đạt DoD cuối.</strong> Có lượt test chức năng PASS nhưng guard từ chối vì <code>.claude.json</code> đổi trong khoảng chạy. Chưa xác định tiến trình ghi. Các quan sát trước thấy thay đổi ở <code>pluginUsage</code>; guard vẫn kiểm toàn file. Không tự dừng phiên khác hoặc hoàn nguyên cấu hình của bạn.</div>
<div class="grid"><div class="card"><strong>__DONE__/__TOTAL__ task</strong><span>gồm 20 task gốc và các task sửa QC</span></div><div class="card"><strong>1 worker · cache off</strong><span>mặc định bàn giao được giữ nguyên</span></div><div class="card"><strong>Chưa có % tăng tốc</strong><span>Full A/B toàn suite chưa được đo</span></div></div>
<nav aria-label="Mục lục"><a href="#before-after">Trước và sau</a><a href="#results">Kết quả kiểm</a><a href="#recommendations">Đề xuất</a><a href="#dod">DoD còn thiếu</a><a href="#rollback">Bật/tắt</a><a href="#raw-samples">Bằng chứng</a></nav>
<section id="before-after"><h2>Hiện tại đã thay đổi gì?</h2><div class="table-wrap"><table><thead><tr><th>Vùng</th><th>Trước</th><th>Source hiện có</th><th>Kỳ vọng, chưa phải số đo</th></tr></thead><tbody>
<tr><th>Chạy test</th><td>Coverage tổng hợp từ nhiều lượt; full cũ bỏ sót pytest function.</td><td>Manifest từng case, đối chiếu JUnit/sidecar, giữ failure và skip provenance.</td><td>Kiểm đủ case trong một job, tránh PASS thiếu bằng chứng.</td></tr>
<tr><th>Tiến trình</th><td>Worker chưa hữu hạn, cô lập và dừng cây con cần kiểm lại.</td><td>1 worker mặc định, 2 worker tùy chọn; HOME/temp riêng, timeout và ownership.</td><td>Giảm tranh chấp; chỉ khuyến nghị 2 worker khi phép đo đạt.</td></tr>
<tr><th>Test lặp</th><td>Thiếu receipt đủ điều kiện dùng lại.</td><td>Reuse/join có fingerprint, eligibility mặc định từ chối và evidence digest.</td><td>Tránh thực thi trùng trong scope đã chứng minh an toàn; vẫn trả chi phí collect/hash/verify.</td></tr>
<tr><th>Readiness</th><td>Probe tĩnh có thể lặp.</td><td>Cache version/inventory; doctor, config, graph và smoke vẫn kiểm trực tiếp.</td><td>Giảm phần lặp tĩnh nếu warm thực tế nhanh hơn off.</td></tr>
<tr><th>Transcript</th><td>Parse lại các file cũ.</td><td>Hash toàn nội dung, cache sự kiện chuẩn hóa từng file, tính lại filter/aggregate.</td><td>Giảm parse; không loại bỏ chi phí đọc/hash, không hứa O(1).</td></tr>
<tr><th>Các lệnh đọc</th><td>Hướng dẫn cũ gọi nối <code>&amp;&amp;</code> là batch.</td><td>Đọc độc lập đồng thời, nhận kết quả riêng từng lệnh; mutation/gate/benchmark giữ thứ tự.</td><td>Giảm số lượt chờ mà không bỏ kiểm tra.</td></tr>
</tbody></table></div></section>
<section id="results"><h2>Những lượt kiểm gần nhất</h2><p>Full đầu tiên trước sửa QC1: 3.579 case, gồm 3.411 pass, 158 fail, 10 skip; thời gian harness 877,400 giây. Có đủ 3.306 case gốc và 273 case mới. Source guard sạch nhưng config guard FAIL. Các dòng khác là gate vùng chạm; không cộng số case vì có thể trùng. Output pytest nguyên văn có thể tính thêm subtest, khác số case chuẩn hóa.</p><p>Sau Full, đã sửa helper project fixture, UTF-8 entrypoint, scanner binary mode và registry luật. Source sau sửa vẫn cần Full chứng nhận; các lượt vùng chạm bị config guard từ chối không được gọi là gate PASS.</p><div class="table-wrap"><table><thead><tr><th>Task</th><th>Output test</th><th>Chứng nhận lượt chạy</th><th>Điểm chặn</th><th>Chi tiết</th></tr></thead><tbody>__ROWS__</tbody></table></div>
<p class="muted">Harness đã bổ sung self-check dependency/browser, ngoài các kiểm tra lỗi đọc snapshot, source drift, đường dẫn dài, Git object readonly, file lock và từ chối đường dẫn ngoài sandbox. Gate FAIL được giữ nguyên, không đổi thành PASS vì child exit 0.</p>
<details><summary>Các lỗi đã tái hiện và sửa</summary><ul><li>JUnit/sidecar không khớp từng case hoặc outcome.</li><li>Skip không có lý do vẫn có thể được coi là PASS/reusable.</li><li>Source/environment thay đổi hoặc publish lỗi có thể làm mất failure provenance.</li><li>Exception chứa payload có thể lọt vào log service.</li><li>Nhãn 2 workers chưa ràng buộc với lệnh khởi chạy thực tế.</li><li>Heartbeat bị truncate khi kill; caller đến muộn không thực sự join.</li><li>Tên file tạm vượt MAX_PATH; cleanup gặp Git object readonly.</li></ul></details>
</section>
<section id="recommendations"><h2>Đề xuất ưu tiên</h2><div class="table-wrap"><table><thead><tr><th>Ưu tiên</th><th>Nên làm gì?</th><th>Lợi ích dự kiến</th><th>DoD để chấp nhận</th></tr></thead><tbody>
<tr><th>Ngay bây giờ</th><td>Tạo khoảng chạy không có phiên khác cập nhật cùng cấu hình Windows, rồi chứng nhận lại gate đang bị config guard chặn.</td><td>Tránh lặp test do nhiễu môi trường; xác định bằng chứng đáng tin cậy.</td><td>Digest các file bảo vệ trước/sau bằng nhau; cleanup và source guard đạt.</td></tr>
<tr><th>Sau khi gate đạt</th><td>Chạy Full fresh, runtime 120 giây/kịch bản, ba cặp Full A/B và ba bộ off/cold/warm mỗi cache.</td><td>Có cơ sở chọn đúng tối ưu cho suite và log thật.</td><td>Parity đầy đủ, giữ mọi mẫu/retry, cùng điều kiện, verify không INVALID.</td></tr>
<tr><th>Có thể áp dụng</th><td>Dùng hướng dẫn batch đọc độc lập; giữ 1 worker và cache off cho tới khi đo xong.</td><td>Giảm lượt chờ giữa các lệnh đọc độc lập.</td><td>Mỗi lệnh có kết quả riêng; không đảo gate, mutation hoặc dependency.</td></tr>
<tr><th>Request tiếp theo</th><td>Xem xét tách metadata usage khỏi cấu hình có ảnh hưởng trong guard, vẫn ghi raw digest audit.</td><td>Giảm false rejection vì biến động <code>pluginUsage</code>.</td><td>Mutation settings/auth/policy vẫn bị chặn; chỉ whitelist đã chứng minh vô hại được ghi nhận riêng. Chưa áp dụng trong request này.</td></tr>
<tr><th>Request tiếp theo</th><td>Dùng digest ngữ nghĩa cho assignment map thay raw SHA của toàn plan.</td><td>Không phải assign lại chỉ vì tick checkbox.</td><td>Checkbox-only không invalid; thay vùng file, dependency hoặc lệnh test bắt buộc invalid.</td></tr>
</tbody></table></div></section>
<section id="dod"><h2>Điều kiện để đóng request</h2><div class="table-wrap"><table><thead><tr><th>DoD</th><th>Nội dung</th><th>Trạng thái và phần còn lại</th></tr></thead><tbody>__DOD__</tbody></table></div>
<p>Ngưỡng khuyến nghị: 2 workers phải giảm median wall time ít nhất 20% với cùng kết quả; cache warm phải nhanh hơn <strong>off</strong>, không chỉ nhanh hơn cold. Không đạt hiệu năng thì giữ serial/off và ghi fallback. Lỗi correctness phải sửa.</p></section>
<section id="limitations"><h2>Giới hạn cần hiểu đúng</h2><ul>
<li>Full đầu tiên FAIL trước QC1; chưa có Full fresh đạt sau sửa hoặc benchmark toàn suite cho source hiện tại. Các phép chạy nhỏ của benchmark là simulation.</li>
<li>Chrome native từng FAIL với thông báo user-data-dir và Target.getTargets hết hạn 90 giây. Acceptance đã chạy native thành công bằng Edge qua tùy chọn công khai <code>--archify-chrome</code>, không tắt sandbox hoặc biến thành skip. Receipt ghi hash browser, Node, entrypoint/package Archify; không chứng minh toàn bộ dependency bắc cầu.</li>
<li>Baseline lịch sử 3206 unittest trong 688,269 giây và inventory hợp nhất 3306 case chỉ dùng tham chiếu; không thay cho kết quả mới.</li>
<li>CPU của toàn cây tiến trình hiện được ghi unavailable; không dùng wall time để giả làm CPU time.</li>
<li>POSIX chưa được chạy trên máy Windows này. Không suy số đo fixture thành phần trăm giảm thời gian toàn session.</li>
<li>Master kiến trúc là snapshot trước sửa QC1, cần refresh khi source cuối ổn định. Lần sinh trước có native browser FAIL được engine chấp nhận bằng Windows elevated fallback; không coi đó là native PASS hoặc chứng nhận source hiện tại.</li>
<li>Thao tác dọn worktree T2.3/LSP bị hệ thống duyệt tự động chặn với lý do “blocked by policy”; đã giữ lại, không thử đường xóa khác.</li>
</ul></section>
<section id="rollback"><h2>Cách giữ trạng thái an toàn khi tiếp tục</h2><pre>python scripts/tdq_test.py tron-bo --repo . --workers 1 --fresh --reuse off --timeout-seconds 1800
Readiness: --readiness-cache off
Transcript: --transcript-cache off</pre><p>Các lệnh trên là lựa chọn rollback/default, không phải kết quả đã chạy. Không cần xóa cache hoặc sửa cấu hình cá nhân để tắt tối ưu. Chưa commit, merge Git, push, release hoặc cập nhật plugin đã cài.</p></section>
<section id="raw-samples"><h2>Mở bằng chứng và tài liệu</h2><ul>__LINKS__</ul><p><a href="checkpoint.json">Dữ liệu checkpoint JSON</a> · <a href="checkpoint.md">Bản Markdown</a></p></section>
<footer>Checkpoint độc lập với báo cáo nghiệm thu cuối. Các receipt thất bại vẫn được giữ; task chưa chứng nhận không được tick hoàn tất.</footer></main></html>'''
    for key, value in {'__SLUG__': esc(SLUG), '__TIME__': esc(now), '__DONE__': str(completed), '__TOTAL__': str(total),
                       '__ROWS__': ''.join(rows), '__DOD__': dod_rows, '__LINKS__': link_html}.items():
        document = document.replace(key, value)
    (OUT / 'checkpoint.html').write_text(document, encoding='utf-8')
    md = [f'# Checkpoint — Kiểm chứng và tăng tốc TDQ Workflow\n',
          'Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md\n',
          f'Cập nhật: {now}. Hoàn tất {completed}/{total} task. Chưa chứng nhận DoD cuối hoặc phần trăm tăng tốc.\n',
          'Full đầu tiên trước QC1: 3579 case, 3411 pass, 158 fail, 10 skip; harness 877.400 giây. Đủ 3306 case gốc + 273 mới. Source guard sạch, config guard FAIL. Sau sửa vẫn cần Full đạt.\n',
          '## Kết quả module\n', '| Task | Output | Gate |', '|---|---|---|']
    for row in tasks:
        md.append(f'| {row["task"]} | {row["cases"]} | {row["status"]} |')
    md += ['\n## Điểm chặn\n', '.claude.json thay đổi trong một số khoảng test. Chưa xác định writer; guard toàn file được giữ nguyên. Cần môi trường ổn định để chứng nhận và chạy Full/benchmark cuối.\n',
           'Chrome native từng lỗi startup/CDP; acceptance chạy native bằng Edge qua --archify-chrome đã thành công. Không đổi sandbox flags. Master kiến trúc vẫn là snapshot trước QC1, cần refresh sau source freeze.\n',
           '## Còn phải làm\n', 'Full fresh; runtime từng kịch bản 120 giây; ba cặp Full A/B; ba bộ off/cold/warm mỗi cache và log thật; QC độc lập cuối; DoD và báo cáo nghiệm thu.\n',
           '## Bản chi tiết\n', '[Mở checkpoint HTML](checkpoint.html). Nội dung HTML có bảng trước/sau, đề xuất, ngưỡng, giới hạn, rollback và liên kết raw receipt.\n']
    (OUT / 'checkpoint.md').write_text('\n'.join(md), encoding='utf-8')
    print(OUT / 'checkpoint.html')


if __name__ == '__main__':
    render()
