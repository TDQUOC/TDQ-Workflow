# QC — Đo độ tuân thủ: bộ skill tiếng Việt so với bộ lai
Ngày: 2026-08-20 · Plan: ../plan/2026-08-19-1903-do-tuan-thu-sau-hybrid.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Bộ chấm đúng | `cd tests && ../.venv/bin/python3 -m pytest test_tdq_eval.py -q` | 109 passed, 139 subtests, 0 skip | PASS |
| Q2 | Không đụng repo thật | `git status --porcelain` | không file nào ngoài đầu ra §2 và hai file sửa trong turn này | PASS |
| Q3 | Chạy đủ | `tdq_eval.py bao-cao --dem` | bản ghi 60 · lỗi chưa xử 0 · chạy lại 0 | PASS |
| Q4 | Đủ độ phủ | `tdq_eval.py bao-cao --phu` | 51 phép kiểm (≥30 đạt); 9/10 ca có ≥3 mã, `duyet-spec-mo-ho` chỉ 2 | FAIL |
| Q5 | Bảng số đầy đủ | `grep -c "^| L" docs/tdq/audit/do-tuan-thu.md` vs `bao-cao` | 17 = 17 | PASS |
| Q6 | Kết luận đúng luật | `grep -n "p =\|độ nhạy" docs/tdq/audit/do-tuan-thu.md` | có cả dòng `p =` lẫn dòng độ nhạy | PASS |
| Q7 | Log service | `TDQ_EVAL_LOG=0 … bao-cao --dem` | 0 dòng log; bật mặc định có timestamp | PASS |
| Q8 | Chi phí | `tdq_eval.py bao-cao --chi-phi` | 37.82 USD / 60 phiên, trần 70 USD | PASS |
| Q9 | Chạy lại được | `tdq_eval.py chay --ca red-green --nhanh viet --lan 1 …` | xong · 0.51 USD · 5 mã chấm được | PASS |
| QC-F1 | Full suite | `cd tests && ../.venv/bin/python3 -m pytest -q` | 1167 passed · 25 failed (đỏ sẵn ở HEAD) | PASS |
| QC-F2 | Hồi quy vùng đã chạm | `pytest test_tdq_eval.py test_build_portable.py -q` | 151 passed, 156 subtests | PASS |
| QC-F3 | Ràng buộc kiến trúc | xem Bằng chứng | 4/4 ràng buộc giữ nguyên | PASS |
| QC-F4 | Clean code | tự kiểm 5 câu | 5/5 "có" | PASS |

## Bằng chứng

### Q1
```
109 passed, 139 subtests passed in 4.48s
$ grep -c "skip" tests/test_tdq_eval.py
0
```

### Q2
```
 M docs/tdq/STATE.md          ← sổ sách state
 M docs/tdq/timing.jsonl      ← sổ sách state
 M docs/workinglog/2026-08-19.md
 M graphify-out/graph.json    ← đầu ra graphify
 M graphify-out/manifest.json ← đầu ra graphify
 M scripts/build_portable.py      ← sửa trong turn này (F-fix, xem dưới)
 M tests/test_build_portable.py   ← sửa trong turn này (F-fix, xem dưới)
?? docs/tdq/{audit,bench,brief,plan,research,spec}/…  ← đúng đầu ra §2
?? evals/ · scripts/tdq_eval.py · tests/mau_transcript/ · tests/test_tdq_eval.py
```
60 phiên đo chạy trong hộp cát riêng (`$TMPDIR/tdq-eval-phien/<ca>__<nhánh>__<lần>/`), có
`HOME`, `CLAUDE_CONFIG_DIR` và git riêng; không phiên nào ghi vào cây làm việc này. Hai file
`build_portable` là do CHÍNH turn QC sửa (bản portable copy nhầm bộ đo), không phải phiên đo.

### Q3
```
bản ghi: 60 · lỗi chưa xử: 0 · chạy lại: 0
```
`grep -rl "hỏng, chạy lại"` trên log của cả vòng chạy: không khớp file nào — đúng 0 lần chạy lại.

### Q4 — FAIL
```
phép kiểm: 51
bao-loi: 6 mã · build-tick-tung-task: 6 · commit-khong-push: 4 · duyet-plan-kem-mode: 7
duyet-plan-thieu-mode: 4 · duyet-spec: 5 · duyet-spec-mo-ho: 2 · lane-mo-ho: 6
mo-request-moi: 6 · red-green: 5
```
Tổng 51 ≥ 30 đạt. Trượt ở vế "mỗi ca ≥ 3 mã": `duyet-spec-mo-ho` chỉ ghép cặp được 2 mã
(L136, L210). Nguyên nhân là bản chất của ca chứ không phải lỗi bộ chấm: ca này đo đúng một
việc — user nói "ok" mơ hồ thì agent phải DỪNG và hỏi lại, không ghi duyệt. Turn đúng luật là
turn KHÔNG ghi file, KHÔNG gọi state, KHÔNG mở brief, nên L149/L218/L121 đều `khong-ap-dung` ở
cả hai nhánh. Đã dò thêm L209, L220, L012 trên chính 6 transcript đó: cả ba cũng
`khong-ap-dung`. Trong bảng mã hiện có (`docs/tdq/audit/luat-hien-co.md`) không còn mã nào áp
được cho ca này, nên không có cách vá nào ở tầng giám khảo. Hai hướng đi tiếp đều đổi phạm vi
đã duyệt nên để user chốt — nêu trong report.

### Q5
```
$ grep -c "^| L" docs/tdq/audit/do-tuan-thu.md → 17
$ tdq_eval.py bao-cao | grep -c "^| L"        → 17
```

### Q6
```
71:1. Bộ mã đăng ký TRƯỚC vòng chạy (28 phép kiểm — 4 xấu · 3 tốt · 21 hoà): p = 0.5000. Đây là con số chốt.
74:p = 0.5000 — kiểm định dấu chính xác một phía, ngưỡng chốt trước khi chạy là 0.05.
84:Với 51 phép kiểm ghép cặp, độ nhạy chỉ đủ để thấy sụt lớn…
```

### Q7
```
$ TDQ_EVAL_LOG=0 .venv/bin/python3 scripts/tdq_eval.py bao-cao --dem
bản ghi: 60 · lỗi chưa xử: 0 · chạy lại: 0
```
Không dòng `[timestamp]` nào. Bỏ biến ra thì có `[2026-08-20T02:09:50] thong-tin: …`.

### Q8
```
chi phí vòng đo: 37.82 USD trên 60 phiên
```
Trần đặt trước: 70 USD. Thêm 0.51 USD của phiên demo Q9 → 38.33 USD.

### Q9
```
$ .venv/bin/python3 scripts/tdq_eval.py chay --ca red-green --nhanh viet --lan 1 \
    --wt /private/tmp/tdq-eval-nhanh --tran-usd 5 --ra <thư mục tạm>
red-green · viet · lần 1: xong · 0.51 USD · L003=dat L005=vi-pham L012=dat L121=vi-pham L210=dat
```
Ghi ra thư mục tạm để 60 bản ghi của vòng chạy chính không bị đè.

### QC-F1
```
25 failed, 1167 passed, 1380 subtests passed in 192.36s
```
25 ca đỏ đều nằm ở `test_skill_router.py::KhoTest::test_moi_duong_dan_khac_rong_deu_mo_duoc`
(skill figma/datarobot của plugin ngoài đã bị gỡ khỏi máy). Đã dựng worktree sạch ở HEAD và
chạy lại đúng file đó: `25 failed, 18 passed` — đỏ sẵn từ trước, không phải do việc này.

### QC-F2
`Chạm:` trong plan gồm `scripts/tdq_eval.py`, `tests/test_tdq_eval.py`, `evals/tuan-thu/`,
`tests/mau_transcript/`; turn QC chạm thêm `scripts/build_portable.py`.
```
pytest test_tdq_eval.py test_build_portable.py -q → 151 passed, 156 subtests passed
```

### QC-F3
- "File code MỚI chỉ nằm trong `scripts/` hoặc `hooks/`": bộ đo là `scripts/tdq_eval.py`.
  `evals/` có 10 json + 14 md + 3 py; ba file `.py` nằm trong `*/seed/` — dữ liệu hộp cát cho
  phiên đo (dự án giả để agent sửa), không file nào của repo import chúng.
- "`scripts/` không import `hooks/`": `grep "import hooks|from hooks|hooks/" scripts/tdq_eval.py`
  → không khớp.
- "Chỉ `tdq_state.py` được ghi `docs/tdq/state.json`": bộ đo không nhắc tới đường dẫn đó;
  `git diff --stat -- docs/tdq/state.json` → rỗng. Mỗi phiên có state riêng trong hộp cát.
- "Thư mục test gọi được mọi tầng": `tests/test_tdq_eval.py` gọi thẳng `tdq_eval` qua `helper`.

### QC-F4 — clean code, 5 câu
- SRP có: mỗi `kiem_L###` chấm đúng một luật; `bao_cao_so` chỉ tính số, `viet_audit` chỉ dựng chữ.
- OCP có: thêm luật = thêm một hàm và một dòng trong `BO_CHAM`, thêm ca = thêm một `ca.json`;
  không phải mở thân hàm nào.
- LSP có: mọi `kiem_*` trả đúng ba giá trị `dat|vi-pham|khong-ap-dung`, không nhánh nào trả None.
- ISP có: `chay_bo` nhận thêm `ghi_lai` và dùng đúng chỗ retry; không tham số nào thừa.
- DIP có: ghi bản ghi vẫn đi qua `_ghi_ban_ghi` sẵn có; loại bộ đo khỏi bản portable dùng đúng
  `EXCLUDE_FILES` sẵn có thay vì thêm nhánh lọc mới.

## Kết luận

FAIL 1/13: Q4 trượt vế "mỗi ca ≥ 3 mã" ở đúng một ca (`duyet-spec-mo-ho`, 2 mã). Không vá được
ở tầng giám khảo; hai hướng còn lại đều đổi phạm vi đã duyệt nên dừng hỏi user (report nêu rõ).
12 hạng mục còn lại PASS kèm bằng chứng lệnh thật.
