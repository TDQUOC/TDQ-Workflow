# RESEARCH — Bằng chứng chuyển giao ECC → TDQ Workflow
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-10-17 · Request: `2026-10-17-1442-de-xuat-nang-cap-tu-ecc`
Phạm vi: khảo sát và đo nền; không triển khai kỹ thuật được đề xuất.

## Bổ sung kiểm định độc lập

QC ultra tái lập tại cùng snapshot: M1 n=12/case có median/p95 ms noop 21.478/22.080, nonconcept 54.270/56.555, LSP 54.812/56.127; ledger LSP=14. Đây là mẫu độc lập, không thay dữ liệu M1 gốc. Smoke valid/malformed/recovery/empty/nonconcept đều exit=0, ledger=2 trong thư mục Unicode+khoảng trắng thật, timeout=120 mỗi con. Giới hạn ASCII của M3 gốc bên dưới vẫn giữ nguyên.

Biên type bổ sung: JSON top-level `null` hoặc `[]` exit=1, `AttributeError`; `read_payload` chỉ bắt lỗi JSON chứ không kiểm kiểu object, trong khi `hooks/scripts/search_observe.py:138-151` và helper dùng `.get`. Đây là giới hạn runtime hiện hữu, không được mô tả thành fail-open cho mọi input; đề nghị kiểm schema/case sai kiểu ở D03/D05 trong request triển khai sau. Không sửa source để làm khảo sát xanh. Evidence độc lập và cách xử lý nguồn sai D06 nằm tại O3 §3.

## 1. Snapshot, môi trường và provenance

| Thành phần | Giá trị đã kiểm |
|---|---|
| TDQ | `C:/Users/admin/Documents/Projects/ForAgentCode/TDQ-Workflow`, HEAD `5c8a9c22a42a59c5a2e0f2941ed92bced36e9df3` |
| ECC | `C:/Users/admin/Documents/ECC`, HEAD `76aaa77df6adc5b889e689007bf99b9a4f74af34` |
| Nhánh TDQ | `feature/de-xuat-nang-cap-tu-ecc`; nhánh gốc request `docs/deep-research-kien-truc-ecc` |
| OS | `Windows-11-10.0.26100-SP0`, Windows 11 Enterprise LTSC 2024 theo môi trường phiên |
| Python | `3.13.15`, MSC v.1944 64 bit AMD64; executable `C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe` |
| PowerShell | `5.1.26100.7705` |
| QC/chế độ | Người dùng chọn `ultra` và `main`; không thêm dịch vụ hoặc model/API runtime |

Trước thực hiện, TDQ đã có thay đổi tracked tại `.tdq-phat-hanh.json`, `STATE.md`, `timing.jsonl` dưới `docs/tdq/` và working log; brief/spec/plan cùng request là untracked. Không coi những thay đổi này là source regression. ECC `git status --short` rỗng. Các phép thử không ghi vào ECC hoặc state request thật.

Nguồn benchmark được đối chiếu với plugin cài tại `C:/Users/admin/.claude/plugins/cache/tdq-local/tdq-workflow/0.71.0`: SHA-256 của `hooks/hooks.json`, `search_observe.py`, `_common.py`, `scripts/tdq_state.py`, `scripts/search_rules.py` giống nhau từng cặp. SHA-256 `hooks/hooks.json`: `4e1bfc6757fdd47925c969c7e09a1c964b82e5435548da530b59137bc3ef90b3`; `search_observe.py`: `f2884c1477c392d25af131540565318d4cd4e327a4f1dbefa12d259f6985cc19`.

LSP đã khởi động Python; references/definition nội bộ file dùng được, import động/xuyên thư mục có lỗi phân giải nên phải đối chiếu thêm manifest và nguồn. Setup báo 7/8 bậc đạt, graph cũ khoảng 1435 phút tại thời điểm kiểm; không dùng graph làm bằng chứng phủ định. Không có `mem0-memory` trong bộ skill khả dụng. Không research web và không đưa khẳng định về CVE hiện hành.

Nhãn bằng chứng:

- **Nguồn:** trực tiếp đọc code/manifest, có vị trí; không đồng nghĩa đã đo runtime.
- **Đo:** chạy entry point thật trong môi trường tạm, có dữ liệu thô.
- **Mô hình:** suy ra từ giả định công khai, chưa phải cải thiện được triển khai.
- **Chưa định lượng:** thiếu dữ liệu thực để ước tính có căn cứ, kèm thiết kế thu thập tiếp.

## 2. Đo nền hook trên Windows

### M1 — Phương pháp

Chạy trong Bash của phiên, dùng `python3 -I -` làm driver stdlib, `subprocess.run` tạo từng tiến trình con. Đo `perf_counter_ns` bao gồm spawn, import, thực thi, capture output và chờ exit; không đo riêng CPU. Mỗi trường hợp 14 lần nối tiếp: lần đầu ghi riêng, bỏ thêm một lần warm-up, giữ 12 mẫu. Timeout mỗi con 5 giây; tất cả exit 0. Không kiểm soát OS cache, không gọi đây là benchmark cold boot.

Ba trường hợp: Python `-I -c pass`; observer với tool `Read` không phải concept; observer với tool `mcp__lsp__find_references`. Hook từ nguồn TDQ, `TDQ_PROJECT_DIR` và cwd trỏ thư mục tạm, `TDQ_LOG=0`, `PYTHONIOENCODING=utf-8`. Con chạy hook như entry point script hiện có, không thêm `-I` cho con vì helper import của script là một phần runtime cần đo; không chạy script ECC/untrusted. Thư mục tạm bị xóa khi kết thúc.

### M1 — Dữ liệu thô, đơn vị ms

| Trường hợp | Lần đầu | Warm-up | 12 mẫu chính |
|---|---:|---:|---|
| Python rỗng | 21.652 | 21.230 | 21.528, 21.325, 21.640, 21.364, 22.459, 21.066, 20.906, 21.329, 21.206, 21.023, 22.178, 21.872 |
| Observer non-concept | 54.537 | 53.749 | 53.876, 54.228, 53.668, 54.847, 54.349, 54.803, 55.681, 55.681, 55.772, 56.006, 55.615, 54.243 |
| Observer LSP | 54.789 | 55.172 | 55.561, 55.644, 55.634, 56.093, 56.248, 54.814, 57.134, 55.681, 56.333, 55.008, 56.830, 56.927 |

| Trường hợp | n | Median ms | p95 nearest-rank ms |
|---|---:|---:|---:|
| Python rỗng | 12 | 21.346 | 22.459 |
| Observer non-concept | 12 | 54.825 | 56.006 |
| Observer LSP | 12 | 55.887 | 57.134 |

Median lấy trung bình hai phần tử giữa, làm tròn 3 chữ số; p95 nearest-rank lấy phần tử `ceil(0.95*n)` sau sắp xếp. Với n=12, p95 chính là max; không ổn định để đặt SLA. Khác biệt giữa hai median observer khoảng 1.062 ms không được coi là chi phí append chính xác do thứ tự và nhiễu chưa được random hóa. Các con observer LSP tạo đúng 14 dòng concept trong ledger tạm; non-concept không tạo dòng. Output stdout rỗng.

Kết luận: chưa có cơ sở cho giả thuyết startup Python 80–150 ms trong brief trên máy này. Median Python rỗng 21.346 ms chỉ là nền spawn; observer khoảng 55 ms có thêm import/helper/I/O, không thể tự động thu hồi tất cả bằng dispatcher. Chưa đo host scheduling hay critical path end-to-end.

### M1 — Lệnh tái lập

Chạy từ repo TDQ bằng Bash; mã driver chỉ nằm trong stdin, không tạo file mã nguồn:

```bash
python3 -I - <<'PY'
import json, os, sys, tempfile, subprocess, time, statistics, pathlib, math
root = pathlib.Path('C:/Users/admin/Documents/Projects/ForAgentCode/TDQ-Workflow')
hook = root / 'hooks/scripts/search_observe.py'
results = {}
env = os.environ.copy()
env.update(TDQ_LOG='0', PYTHONIOENCODING='utf-8')
with tempfile.TemporaryDirectory(prefix='tdq-ecc-bench-') as tmp:
    env['TDQ_PROJECT_DIR'] = tmp
    base = dict(cwd=tmp, session_id='isolated-benchmark', hook_event_name='PostToolUse', tool_name='Read', tool_input={})
    cases = [('python_noop', [sys.executable, '-I', '-c', 'pass'], None),
             ('observer_nonconcept', [sys.executable, str(hook)], json.dumps(base)),
             ('observer_lsp', [sys.executable, str(hook)], json.dumps(dict(base, tool_name='mcp__lsp__find_references')))]
    for name, cmd, payload in cases:
        values = []
        for _ in range(14):
            start = time.perf_counter_ns()
            proc = subprocess.run(cmd, input=payload, text=True, capture_output=True,
                                  env=env, cwd=tmp, timeout=5)
            if proc.returncode:
                raise RuntimeError((name, proc.returncode, proc.stderr))
            values.append(round((time.perf_counter_ns()-start)/1e6, 3))
        sample = values[2:]
        results[name] = dict(first_ms=values[0], warmup_ms=values[1], samples_ms=sample,
                             n=len(sample), median_ms=round(statistics.median(sample), 3),
                             p95_nearest_rank_ms=sorted(sample)[math.ceil(.95*len(sample))-1])
    rows = [json.loads(x) for x in (pathlib.Path(tmp)/'docs/tdq/.tdq-search.jsonl').read_text(encoding='utf-8').splitlines()]
    results['isolation'] = dict(ledger_rows=len(rows), concept_rows=sum(x.get('loai')=='khai_niem' for x in rows))
print(json.dumps(results, ensure_ascii=False, indent=2))
PY
```

Lần thử driver đa dòng qua PowerShell kết thúc không có output; không dùng lần đó làm phép đo. Chỉ bảng JSON thật của lần Bash phía trên được lấy số.

### M2 — Matcher thực, không cộng hook tưởng tượng

Đếm từ `hooks/hooks.json:38-112` bằng `re.search(matcher, tool_name)` theo tập tên công cụ ở bảng. Đây là đối chiếu manifest, không phải trace host thực thi. Một command được đếm là một entry process dự kiến; host có thể chạy đồng thời và tool name có thể được adapter biến đổi.

| Tool | PreToolUse commands | PostToolUse commands | Ghi chú |
|---|---:|---:|---|
| Read | 1 | 0 | read_gate |
| Edit / Write | 1 | 0 | edit_gate, không phải ba hook Python |
| Bash | 2 | 1 | bash_gate + search_gate, sau đó search_observe |
| PowerShell | 1 | 0 | search_gate có matcher, bash_gate và post observer không có |
| Grep | 1 | 0 | search_gate |
| mcp__lsp__find_references | 1 | 1 | search_observe ở pre và post |

`mcp__lsp__start_lsp` còn khớp lsp_gate và observer tại pre; không đồng nhất nó với mọi LSP call. `UserPromptSubmit` có hai commands (`prompt_context`, `search_observe`) tại `hooks/hooks.json:24-35`. Mỗi sự kiện cần đánh giá riêng.

Lệnh đã chạy: driver Python đọc JSON, lặp hai event × các tool, chọn entry bằng `re.search`, đếm hook `type=command`. Không chạy hook trong phép đếm. Hai observer pre/post cho LSP là chủ đích chịu lỗi call thất bại, được giải thích tại `hooks/scripts/search_observe.py:7-12`; không xóa một phía chỉ vì thấy trùng.

## 3. Smoke và biên runtime hiện có

### M3 — Hook observer hợp lệ → input lỗi → phục hồi

Chạy entry point thật `hooks/scripts/search_observe.py`, mỗi con timeout 120 giây, cwd/TDQ_PROJECT_DIR là thư mục tạm có khoảng trắng. Tên prefix `tdq Unicode ` là chữ ASCII; **chưa chứng minh đường dẫn Unicode**. Ba payload nối tiếp: JSON LSP hợp lệ, `{invalid`, JSON hợp lệ. Output:

| Case | Exit | Thời gian ms | stdout/stderr |
|---|---:|---:|---|
| valid | 0 | 55.676 | rỗng/rỗng |
| malformed | 0 | 54.077 | rỗng/rỗng |
| recovery | 0 | 54.099 | rỗng/rỗng |

Ledger cuối có đúng 2 dòng `loai=khai_niem`, `cong_cu=lsp:find_references`, `khoa=phien:smoke`. Payload lỗi được helper chuyển thành `{}` (`hooks/scripts/_common.py:97-101`) và không tạo concept. Đây là fail-open có chủ đích cho observer, **không phải bằng chứng parser an toàn fail-closed**.

Một assertion ban đầu kỳ vọng sai `cong_cu=lsp` đã thất bại; đã đối chiếu `scripts/search_rules.py:646-656`, sửa oracle thành `lsp:find_references` rồi chạy lại. Không thay runtime hoặc đổi input để ép kết quả. Không coi lỗi oracle này là bug sản phẩm.

Tái lập: dùng driver M1 với 3 subprocess, payload valid như M1 nhưng session `smoke`; lần giữa input `{invalid`; timeout=120. Assert return code đều 0; đọc ledger và assert đúng hai dòng/schema nói trên. Tiến trình hook thật đã chạy nhưng không có dịch vụ mới sống lâu; runtime test ứng dụng mới không áp dụng cho tài liệu.

### M4 — PowerShell/Bash phân biệt code và chuỗi

Gọi hàm thật `search_rules.la_goi_khai_niem` trong memory, không thực thi câu lệnh input. Bốn đầu vào và output:

```text
PowerShell: graphify query startup -> graphify:query
PowerShell: Write-Output "graphify query startup" -> None
Bash: graphify query startup -> graphify:query
Bash: printf "graphify query startup" -> None
```

Nguồn `scripts/search_rules.py:646-668`. Hàm đã nhận PowerShell; điểm thiếu ở M2 là **đăng ký post observer**, không thể kết luận TDQ hoàn toàn không hiểu PowerShell.

Lệnh tái lập: `python3 -I -` rồi thêm `root/'scripts'` vào `sys.path`, import `search_rules`, gọi bốn cặp `(tool, command)` trên và assert kết quả. Tất cả assert đạt; không ghi file/state.

### M5 — Kiểm vùng chạm trước khi tạo tài liệu

Gọi `tdq_test.ban_kinh([path], repo)` cho O1/O2/O3 đều trả `([], None)`: không có module unit test tự động được selector gán cho ba đường dẫn mới. Vì vậy lint xanh hoặc `vung-cham` chạy rỗng không chứng minh báo cáo đúng; cần QC nguồn/ngữ nghĩa và suite hiện có riêng. Không thêm test chỉ tìm từ khóa để tạo xanh giả.

## 4. Hồ sơ nguồn theo trụ cột

Các đường dẫn ECC dưới đây tương đối với snapshot ECC; TDQ tương đối với repo hiện tại. Nhãn **Nguồn** nghĩa là xác minh tĩnh, không phải thử nghiệm ECC. Agent khảo sát chỉ đọc trả nguồn; leader đối chiếu các điểm quyết định, không nhận nguyên đề xuất khi trái spec.

| ID | Trụ cột | TDQ — bằng chứng và quan hệ | ECC — kỹ thuật đối chiếu | Kết luận chuyển giao |
|---|---|---|---|---|
| E-H1 | Hooks | `hooks/hooks.json:38-112`: matcher chọn từng command; M2 cho thấy Bash pre có hai command, Edit chỉ một | `scripts/hooks/bash-hook-dispatcher.js:22-52,123-174`: danh sách module `.run(rawInput)`, gom context và xử lý kết quả cùng process | Chỉ thử gom các hook thực cùng sự kiện; không kỳ vọng giảm process trên mọi Edit/Read |
| E-H2 | Hooks | `hooks/scripts/search_gate.py:43-44,126-129`: breaker chỉ ở nhánh thiếu readiness stamp; `edit_gate.py` giữ kỷ luật tick/team | `scripts/hooks/gateguard-fact-force.js:1613-1634`: rút ngắn denial lặp; `:1721-1723` có trivial exemption | Học dedupe/rút ngắn thông báo, không tự đổi deny thành allow; không bỏ task/team/gate duyệt |
| E-H3 | Hooks | Chưa có cơ sở chứng minh cần một trivial bypass mới; tài liệu đã có xử lý riêng trong edit gate | `scripts/lib/gateguard-code-lexer.js:307-315`: so `codeSignature` sau lexer | Không nhập bypass dựa vào xóa whitespace/comment; Python indentation, encoding/shebang và directive có thể mang ngữ nghĩa |
| E-S1 | Shell | `scripts/search_rules.py:159-242`: tách subshell/heredoc, cap depth; `:646-668` có PowerShell recognition | `scripts/hooks/lib/shell-scan.js:6-12`: budget `24*(L+1)+4096`; `scripts/hooks/block-no-verify.js:136-157` xét cờ ngắn theo scanner | TDQ đã có parser phục vụ nhận diện tìm kiếm; thêm ngân sách tổng và trạng thái unknown, không gọi nó là sandbox an toàn shell |
| E-W1 | Windows | `hooks/hooks.json:58-71,104-110`: search_gate có PowerShell, bash_gate/post observer không có; M4 xác minh hàm hiểu PowerShell | `scripts/lib/windows-bash.js:19-46,57-85`: loại WSL launcher khỏi lựa chọn Git Bash | Ưu tiên độ phủ adapter, inventory executable và test đường dẫn; chỉ thêm selector khi TDQ thật sự phải chọn Bash |
| E-W2 | Windows | TDQ dùng Python, có UTF-8 helper (`hooks/scripts/_common.py:19-29`); không đủ bằng chứng cho Node `.cmd` injection trên TDQ | `scripts/hooks/pre-bash-commit-quality.js:263-307`: đường spawn Windows cụ thể dùng env token và `windowsVerbatimArguments` | Đọc điều kiện CVE như threat-model tham khảo; không sao chép bản vá Node vào Python hoặc kết luận TDQ mắc CVE |
| E-T1 | Team | `scripts/tdq_team.py:215-238,264-312`: b-level trên DAG, chia wave theo `Cần:` và giao tập file; M6 tái lập | `scripts/lib/agent-proximity/distance.js:1-315`: overlap, dependency và tree proximity kết hợp noisy-OR | TCAS chỉ nên bổ sung advisory cho quan hệ chưa khai; không thay khóa cùng-file và DAG hiện có |
| E-T2 | Fingerprint | `scripts/tdq_state.py:569-589` băm thân sau heading; `scripts/tdq_team.py:345-350,375-377,396` băm toàn file plan | `scripts/lib/context-carriers.js:146-170`: tách registry/profile/compiler/plan/adapter/content digest và tạo carrierDigest từ value; dòng 165 yêu cầu tái kiểm nguồn khi materialize. Đây là nguyên tắc định danh theo mục đích, không phải implementation assignment/progress hash của TDQ | TDQ đã có fingerprint; cần tách hash approval, assignment và progress, không đổi mọi hash sang body hash một cách máy móc |
| E-T3 | Worktree | `scripts/tdq_team.py:662-744,804-825,833-898`: kiểm dirty/merged, lifecycle và conflict probe | `scripts/lib/worktree-lifecycle/lifecycle.js:16-61`; `scripts/lib/worktree-lifecycle/git.js:125-144`: trạng thái và `merge-tree --write-tree --name-only` | Có thể học phân loại trạng thái và exit-code rõ; hiện đại hóa probe sau khi test Git tương thích, không giả định mọi nonzero là conflict |
| E-T4 | Cache | `scripts/tdq_team.py:698-700` bỏ qua rác tái sinh, không phải cache; `:931-951` chuẩn hóa test theo runtime host | `ecc2/src/worktree/mod.rs:1200-1405`: fingerprint file manifest/lock và shared directory symlink, tháo khi hash lệch | Lockfile không bảo vệ quyền ghi/ABI/toolchain; không dùng symlink/junction venv hoặc node_modules ghi được làm mặc định |
| E-Q1 | Review | `skills/tdq-build/references/qc.md:34-40,73-84,97-110`: TDQ đã có ultra độc lập và evidence | `workflows/orch-review.workflow.js:64-108,220-239,245-287`: schema findings, dedup, skeptic và fail-closed | Học schema outcome và giữ unresolved; không thêm agent cho mọi lỗi nhỏ hoặc lấy confidence làm ground truth |
| E-Q2 | Artifact | `tests/test_report_kien_truc_ecc.py:211-225`: thiếu báo cáo thật thì validate fixture rồi return | `workflows/orch-review.workflow.js:248-255,280-283`: lỗi/null verifier hoặc dimension thiếu không được APPROVE | Tách validator unit test khỏi artifact acceptance; fixture xanh không chứng minh artifact có mặt |
| E-Q3 | Approval | `hooks/scripts/prompt_context.py:40-83,91-117,209-221,304-312`: regex dựa prompt text rồi phát nhắc; M7 kiểm hàm thuần | ECC review schema là gợi ý phân biệt trusted input/analysis outcome, không trực tiếp giải quyết host provenance | Cần adapter phân loại nguồn tin và hồi quy ngôn ngữ; không lấy text trong notification làm quyền duyệt |

### M6 — Bộ chia wave thật, dữ liệu synthetic có oracle

Gọi `tdq_team.Task`, `quyet_dinh_task` và `chia_dot` trong memory (không CLI/state/Git). Task A chạm `core.py`; B chạm `helper.py`, khai `Cần: T1.1`; C chạm `core.py`. Output thật:

```json
{"decisions":{"T1.1":["giao",""],"T1.2":["giao",""],"T1.3":["giao",""]},"waves":{"T1.1":1,"T1.3":2,"T1.2":2}}
```

Assert A/C khác wave và B sau A đều đạt. Đây là dữ liệu kiểm thuật toán, không phải lịch sử task thật hoặc tỷ lệ conflict. TDQ không chỉ có so sánh chuỗi file đơn giản: đã có DAG và critical-path metadata.

Lệnh tái lập: Python `-I -`, thêm `root/scripts` vào `sys.path`, import `tdq_team`; tạo ba `Task(ma, ' ', 'P1')`, đặt `vung_file` và `text` như mô tả; gọi `quyet={t.ma:quyet_dinh_task(t,tasks) for t in tasks}`, rồi `chia_dot(tasks,quyet)`. Không có write trong đường tính này.

### M7 — Ranh giới nhận diện duyệt, không ghi state

Gọi hàm thật `prompt_context.looks_like_approval(text,target)` qua import `hooks/scripts` trong Python `-I`; không gọi main hook hoặc CLI duyệt. Output:

| Text đầu vào | target | recognized |
|---|---|---|
| `duyệt spec` | spec | true |
| `duyệt plan` | plan | true |
| `1a` | mode | false |
| `inline` | mode | true |
| `Spec approved` | spec | true |
| Chuỗi XML notification chứa `spec approved` | spec | true |
| `Chưa duyệt spec` | spec | false |
| `duyệt spec nhưng sửa thêm` | spec | false |

Không lưu raw notification như lệnh cần làm. Hàm không biết provenance; nó cũng không nhận `1a` trong khi hướng dẫn chat yêu cầu dạng số+chữ (`LETTER` chỉ a–d đứng riêng ở dòng 80–83). Đã quan sát trong phiên: hook từng phát nhắc duyệt sai khi nhận notification, và nhắc “không rõ phê duyệt” cho câu người dùng rõ ràng. Tuy nhiên **leader không chạy duyệt theo notification**; state không bị duyệt giả trong phiên này. Vì hàm thuần nhận đúng câu tiếng Việt, nguyên nhân lớp serialization/adapter của false-negative đó chưa được xác minh. Không quy kết do state đã chuyển phase hoặc do từ điển không hiểu tiếng Việt.

Đề xuất phải dựa vào nguồn tin đáng tin do host/adapter cấp nếu có. Prefix blacklist XML/`Task completed` chỉ là lớp phụ, không đủ phân biệt mọi nguồn; người dùng có thể trích câu duyệt để hỏi. Không biến regex nhận diện thành cơ chế tự động cấp quyền.

### Thuật toán ECC và giới hạn khi chuyển

- **TCAS:** `R=1−Π(1−w_i*r_i)`, trọng số kênh `[1.0,0.9,0.25]`; overlap dùng hệ số trên khoảng dòng, dependency BFS với suy giảm khoảng cách và cap, tree dùng LCA. Ngưỡng advisory/resolution trong nguồn là heuristic ECC, không phải xác suất conflict của TDQ. Quan hệ import không tự suy ra thứ tự task và có thể tạo chu kỳ nếu ép thành DAG.
- **Fingerprint:** thay `sha_file` bằng `sha256_noi_dung` mới chỉ bỏ metadata header, **không** bỏ checkbox task hoặc nội dung tiến độ. Đề xuất “thay hai dòng là hết stale” không đủ căn cứ. Phải định nghĩa vùng assignment gồm task ID, `Chạm:`, `Cần:`, hợp đồng/test và version schema; hash approval vẫn giữ ngữ nghĩa đã duyệt.
- **Skeptic:** ECC chỉ verify finding blocking, `isReal=true` là confirmed; `isReal=false` chỉ refuted khi confidence >=0.8; uncertain/unverified vẫn blocking, dimension lỗi khiến CHANGES_REQUESTED. Ngưỡng 0.8 là heuristic của ECC, không phải độ chính xác 80%. Học yêu cầu bằng chứng phản bác và outcome rõ, chưa đề xuất nhập cứng ngưỡng số đó.
- **Denial:** chỉ rút ngắn thông điệp, giữ nguyên quyết định an toàn. Không nhận đề xuất “sau ba lần nhả block”, blanket fail-open dispatcher hoặc trivial whitespace bypass vì trái scope/ràng buộc.
- **Scanner:** budget giới hạn công việc mà nó đếm; không chứng minh mọi regex/helper đều được bao phủ hoặc chặn mọi tấn công. Hằng số ECC `24*(L+1)+4096` không phải `24L+4096`; chỉ dùng tham khảo, phải benchmark parser Python riêng.
- **Cache:** fingerprint khớp chỉ là điều kiện cần. Mutable symlink có thể làm bẩn main/dependency của agent khác, và `.venv` có thể chứa đường dẫn tuyệt đối; không có cache an toàn mặc định chỉ bằng hash lockfile.

## 5. Thiết kế ước tính, đơn vị và giới hạn

- Hook: `T_tiết_kiệm_thành_phần = N × k × startup − overhead_dispatch`; `N` là số event liên quan, `k` số process thực giảm. Giá trị âm không được cắt bỏ để làm đẹp ROI. Nếu host song song, đo critical path, không cộng tổng duration.
- Cache: `T_lợi = install_tránh_được − kiểm_cache − cô_lập − bảo_trì_phân_bổ`. Repo không có manifest dependency nặng tại gốc theo glob; không suy ra mọi consumer TDQ đều nhẹ. Lợi ích cho consumer khác chưa định lượng.
- Review: `precision=TP/(TP+FP)`, `recall=TP/(TP+FN)`. Chưa có corpus lỗi có nhãn độc lập và lịch sử đầy đủ; không gán tỷ lệ tăng chất lượng từ ngưỡng confidence của ECC.
- Scheduling: thời gian đường găng và số va chạm thật cần lịch sử/trace có nhãn; ví dụ nhỏ chỉ chứng minh hành vi thuật toán, không suy ra mức giảm xung đột phần trăm.
- Giờ người triển khai/duy trì là ước lượng kỹ thuật với giả định, tách hoàn toàn thời gian máy. Tiền/token chưa đủ đầu vào để lượng hóa. ROI theo thời gian máy chỉ có ý nghĩa nếu thời gian đó đang chặn công việc; không coi một giây máy là một giây người.
- Kịch bản thấp/cơ sở/cao phải công khai các đầu vào giả định và gọi là mô hình, không phải số cải thiện đã đo. Không cộng tiết kiệm dispatcher và observer pruning nếu chúng loại cùng một tiến trình.

Không chạy ECC code, exploit, lệnh phá hoại, cài dependency hoặc test trên state thật. Không kết luận TDQ có CVE, chặn được mọi shell, hoặc chắc chắn giảm xung đột/chất lượng theo một phần trăm chưa đo.
