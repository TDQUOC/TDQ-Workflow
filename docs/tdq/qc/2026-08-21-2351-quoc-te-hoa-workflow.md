# QC — Quốc tế hoá bộ workflow TDQ
Ngày: 2026-08-22 · Plan: ../plan/2026-08-21-2351-quoc-te-hoa-workflow.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | state giữ ngôn ngữ | `tdq_state.py init <slug> full` / `... --lang en` trong 2 thư mục tạm | `doc_lang='vi'` khi thiếu cờ · `doc_lang='en'` khi có cờ | PASS |
| Q2 | đường cũ còn sống | `pytest tests/test_prompt_context.py -q` | 21 passed, 68 subtests | PASS |
| Q3 | đường mới (4 cổng) | `pytest tests/test_prompt_context.py -q -k "english or letter"` | 9 passed, 57 subtests | PASS |
| Q4 | đường phải chặn | `pytest tests/test_prompt_context.py -q -k reject` | 5 passed, 23 subtests | PASS |
| Q5 | chuỗi máy | `i18n_check.py --kind string hooks/ scripts/` | 0 dòng / 34 file, exit 0 | PASS |
| Q6 | comment mã nguồn | `i18n_check.py --kind comment hooks/ scripts/` | vòng 1: 1 dòng (`doc_lint.py:80`) → fix QC1.1 → 0 dòng | PASS (sau fix) |
| Q7 | thân luật | `i18n_check.py skills/ agents/` | 0 dòng / 47 file, exit 0 | PASS |
| Q8 | giữ hành vi | đếm mã `TDQ:<CODE>` + so danh sách lệnh con `tdq_state.py` với HEAD | 10 mã giữ nguyên số đếm · lệnh con y hệt | PASS |
| Q9 | giữ soul | `git diff --stat` + so tiêu đề `soul.md` với HEAD | cùng 4 nguyên tắc, cùng thứ tự mục, vế ưu tiên nguyên văn | PASS |
| Q10 | luật ngôn ngữ mới | đọc `tdq-conventions/SKILL.md` mục `## 0. Language` | bảng đủ 3 tầng + dòng mặc định `vi` | PASS |
| Q11a | lưới test | `pytest tests/ -q` | 37 failed, 1198 passed — đúng 37 lỗi `test_skill_router.py` của mốc | PASS |
| Q11b | lưới eval | (chưa chạy) | KHÔNG CHẠY — cần user duyệt chi phí, xem mục dưới | FAIL |
| Q12 | bản sinh | `tdq_checkportable.py check --root portable_claude` / `--root portable_codex` | CLEAN 84 file · CLEAN 129 file | PASS |
| Q13 | log service | 3 CLI chạy có/không `TDQ_LOG=0` | `i18n_check` · `doc_lint` · `skill_tokens` đều in `[timestamp]`, cờ tắt làm im | PASS |
| Q14 | hồ sơ kiến trúc | `grep "2026-08-22" docs/kien-truc.md` | dòng 51: quyết định ngôn ngữ 3 tầng | PASS |
| F1 | full suite | `pytest tests/ -q > /tmp/qc-run.log` | 37 failed, 1198 passed, 1437 subtests (87s) — 0 lỗi mới | PASS |
| F2 | hồi quy vùng chạm | full suite phủ 14 dòng `Chạm:`; test module chạy ngay trong từng task | không node nào thiếu test | PASS |
| F3 | ràng buộc kiến trúc | 5 phép đếm ở mục Bằng chứng | 5/5 giữ nguyên | PASS |
| F4 | clean code | 5 câu tự kiểm SOLID | 5/5 "có", không phải sửa gì | PASS |

## Bằng chứng

### Q1
```
✅ init: request=2026-08-22-0300-qc-kiem-ngon-ngu lane=full phase=idle
doc_lang= 'vi'
✅ init: request=2026-08-22-0300-qc-kiem-ngon-ngu lane=full phase=idle
doc_lang= 'en'
```

### Q5 · Q6 · Q7
```
0 Vietnamese line(s) in 34 file(s)      # --kind string
scripts/doc_lint.py:80: [comment] # Chú thích HTML không phải câu văn: ...   → QC1.1
0 Vietnamese line(s) in 34 file(s)      # --kind comment, sau fix
0 Vietnamese line(s) in 47 file(s)      # skills/ agents/
```

### Q8
```
13 TDQ:APPROVE · 9 TDQ:STATE · 8 TDQ:GIT · 7 TDQ:TICK · 7 TDQ:LOG · 6 TDQ:TEAM
5 TDQ:NEXT · 3 TDQ:OUTPUT · 1 TDQ:INTAKE   (y hệt HEAD)
HEAD: ['approve','get','init','next','phases-doc','reset','set']
NOW : ['approve','get','init','next','phases-doc','reset','set']  same: True
```
Chỉ `TDQ:` trần lệch 8 → 9: thêm một lần nhắc trong câu văn/regex, không phải mã nhắc mới.

### Q11a · F1
```
37 failed, 1198 passed, 1437 subtests passed in 87.30s (0:01:27)
Toàn bộ 37 FAILED nằm ở tests/test_skill_router.py — đúng mốc T1.1.
```

### Q11b — vì sao FAIL
Bộ `evals/tuan-thu` là lưới DUY NHẤT đo hành vi model sau khi dịch luật. Không chấm lại
được từ 60 bản ghi cũ vì transcript của chúng nằm ở `/private/tmp` và đã bị xoá; chấm lại
trực tiếp nghĩa là chạy 72 phiên `claude -p` opus (~70 USD, vài giờ), và `NHANH` đang ghim
2 commit cũ nên chưa có nhánh cho cây đã dịch. Đây là input chỉ user có (duyệt chi phí).
Đã chạy 1 phiên khói trên cây đã dịch, ca `duyet-spec-tieng-anh`: L149/L275/L012/L210 ĐẠT,
L121 vi-phạm — nằm trong dải nhiễu của 6 bản ghi `duyet-spec` cũ.
Lệnh để chạy đầy đủ khi user duyệt:
```
python3 scripts/tdq_eval.py chay --nhanh ca-hai --lan 3 --wt /private/tmp/tdq-eval-nhanh \
  --tran-usd 70 --tiep-tuc
```

### F3
```
scripts/ import hooks/            : 0 file
skills/*.md chép thân script      : 0 dòng
ghi docs/tdq/state.json           : chỉ scripts/tdq_state.py:393 (_atomic_write)
portable_claude / portable_codex  : sinh lại bằng build_portable.py, checkportable CLEAN
hub main()/cli()/log()            : 14 dòng `Chạm:` khai đủ, full suite xanh ngoài mốc
```

### F4
```
SRP có · OCP có · LSP có · ISP có · DIP có
```
Thay đổi mã nguồn vòng này chỉ gồm: một chú thích trong `scripts/doc_lint.py` (QC1.1) và
các neo test song ngữ — không thêm hàm, không đổi luồng, không phải sửa gì sau tự kiểm.

## Kết luận
FAIL: Q11b (lưới eval hành vi) — chưa chạy được vì cần user duyệt chi phí ~70 USD.
17/18 hạng mục PASS; Q6 PASS sau fix QC1.1. Không thêm task fix nào khác vào plan vì
hạng mục còn lại bị chặn bởi quyết định của user, không phải bởi lỗi mã.
