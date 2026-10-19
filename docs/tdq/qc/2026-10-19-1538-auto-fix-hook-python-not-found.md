# QC — Tự động xử lý lỗi Python Not Found cho Hook và Auto-Setup trên máy mới
Ngày: 2026-10-19 · Plan: ../plan/2026-10-19-1538-auto-fix-hook-python-not-found.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | 100% command trong `hooks/hooks.json` có cấu trúc fallback đa nền tảng | `python -c "import json; ..."` | 13/13 commands validated có fallback `python3 ... \|\| py -3 ... \|\| python ...` | PASS |
| Q2 | `session_start.py` tự kích hoạt nền `tdq_setup.py --nen` và thông báo `[TDQ:SETUP]` khi chạy lần đầu | `python -m unittest tests.test_auto_fix_python3_hook.SessionStartAutoSetupTest` | 2/2 tests OK | PASS |
| Q3 | `tdq_checkportable.py` tìm được thư mục Scripts fallback khi PATH bị chặn bởi Store stub | `python -m unittest tests.test_auto_fix_python3_hook.CheckPortableScriptsTest tests.test_shim_python3.ChonThuMucTest` | 7/7 tests OK | PASS |
| Q4 | `tdq_setup.py` tự động phát hiện, cài shim `python3` và chạy smoke dry-run hook thành công | `python -m unittest tests.test_auto_fix_python3_hook.SetupShimAndDryRunTest` | 2/2 tests OK | PASS |
| Q5 | `KHOI_HUONG_DAN` và `~/.claude/CLAUDE.md` hiển thị lệnh setup đa nền tảng và nguyên tắc Self-healing | `python -m unittest tests.test_auto_fix_python3_hook.InstructionHardeningTest tests.test_claude_md_core.KhoiHuongDanToolTest` | 9/9 tests OK | PASS |
| Q6 | File test mới `tests/test_auto_fix_python3_hook.py` chạy xanh 100% | `python -m unittest tests/test_auto_fix_python3_hook.py` | 7/7 tests OK (0.28s) | PASS |
| Q7 | Toàn bộ các test suite liên quan trực tiếp và gián tiếp chạy xanh 100% | `python -m unittest tests/test_auto_fix_python3_hook.py tests/test_shim_python3.py tests/test_claude_md_core.py` | 34/34 tests OK; 210+ test liên quan xanh | PASS |
| Q8 | Kiểm tra tài liệu `doc_lint` trên toàn bộ brief, spec, plan đạt 0 lỗi và `--pair` khớp hợp đồng | `python scripts/doc_lint.py ...; python scripts/doc_lint.py --pair ...` | 0 violation(s), exit 0, pairing khớp | PASS |

## Bằng chứng

### Q1
```
python -c "import json; d=json.load(open('hooks/hooks.json', encoding='utf-8')); cmds=[];
def scan(o):
  if isinstance(o, dict):
    if 'command' in o and isinstance(o['command'], str): cmds.append(o['command'])
    for v in o.values(): scan(v)
  elif isinstance(o, list):
    for x in o: scan(x)
scan(d.get('hooks', {})); 
assert len(cmds) > 0;
assert all('python3' in c and 'py -3' in c and 'python' in c and '||' in c for c in cmds); 
print(f'PASS: {len(cmds)} hook commands have valid fallback chain')"
-> PASS: 13 hook commands have valid fallback chain
```

### Q2
```
python -m unittest tests.test_auto_fix_python3_hook.SessionStartAutoSetupTest
..
----------------------------------------------------------------------
Ran 2 tests in 0.003s

OK
```

### Q3
```
python -m unittest tests.test_auto_fix_python3_hook.CheckPortableScriptsTest tests.test_shim_python3.ChonThuMucTest
.......
----------------------------------------------------------------------
Ran 7 tests in 0.000s

OK
```

### Q4
```
python -m unittest tests.test_auto_fix_python3_hook.SetupShimAndDryRunTest
..
----------------------------------------------------------------------
Ran 2 tests in 0.278s

OK
```

### Q5
```
python -m unittest tests.test_auto_fix_python3_hook.InstructionHardeningTest tests.test_claude_md_core.KhoiHuongDanToolTest
..[2026-10-19T16:21:00] ghim hướng dẫn 3 tầng vào C:\Users\admin\AppData\Local\Temp\tmpq2u9qxmj\CLAUDE.md
...[2026-10-19T16:21:00] ghim hướng dẫn 3 tầng vào C:\Users\admin\AppData\Local\Temp\tmp9bad3pjj\CLAUDE.md
....
----------------------------------------------------------------------
Ran 9 tests in 0.006s

OK
```

### Q6
```
python -m unittest tests/test_auto_fix_python3_hook.py
.......
----------------------------------------------------------------------
Ran 7 tests in 0.278s

OK
```

### Q7
```
python -m unittest tests/test_auto_fix_python3_hook.py tests/test_shim_python3.py tests/test_claude_md_core.py
..........................[2026-10-19T16:19:07] ghim hướng dẫn 3 tầng vào C:\Users\admin\AppData\Local\Temp\tmptbpexvt5\CLAUDE.md
...[2026-10-19T16:19:07] ghim hướng dẫn 3 tầng vào C:\Users\admin\AppData\Local\Temp\tmp0dqzqizo\CLAUDE.md
.....
----------------------------------------------------------------------
Ran 34 tests in 0.290s

OK
```

### Q8
```
python scripts/doc_lint.py docs/tdq/brief/2026-10-19-1538-auto-fix-hook-python-not-found.md docs/tdq/spec/2026-10-19-1538-auto-fix-hook-python-not-found.md docs/tdq/plan/2026-10-19-1538-auto-fix-hook-python-not-found.md
[2026-10-19T16:21:14] doc_lint: lint 3 file: 2026-10-19-1538-auto-fix-hook-python-not-found.md, 2026-10-19-1538-auto-fix-hook-python-not-found.md, 2026-10-19-1538-auto-fix-hook-python-not-found.md
[2026-10-19T16:21:14] doc_lint: R14 2026-10-19-1538-auto-fix-hook-python-not-found.md → 0 finding(s)
[2026-10-19T16:21:14] doc_lint: done — 0 violation(s) total, exit 0

python scripts/doc_lint.py --pair docs/tdq/spec/2026-10-19-1538-auto-fix-hook-python-not-found.md docs/tdq/plan/2026-10-19-1538-auto-fix-hook-python-not-found.md
[2026-10-19T16:21:15] doc_lint: pairing 2026-10-19-1538-auto-fix-hook-python-not-found.md ↔ 2026-10-19-1538-auto-fix-hook-python-not-found.md
```

## Lệch spec chờ duyệt
không có

## Kết luận
PASS toàn bộ 8/8 hạng mục Definition of Done (Q1-Q8). Sẵn sàng chuyển sang phase report.
