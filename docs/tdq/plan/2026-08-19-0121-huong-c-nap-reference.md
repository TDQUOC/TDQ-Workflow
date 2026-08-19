# PLAN — Hướng C: nạp reference theo nhu cầu

Ngày: 2026-08-19 · Spec: ../spec/2026-08-19-0121-huong-c-nap-reference.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — user chọn A lúc duyệt plan
Trạng thái plan: HOÀN THÀNH

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo trong cùng một nhánh.
2. Mỗi task: đánh `[~]` khi bắt đầu → chạy check trước (đỏ) → làm → check xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm ·
   `[>]` đã giao agent con · `[x]` xong.
3. Sau mỗi phase: chạy test của module đang sửa, phải xanh mới sang phase sau. Full suite
   chạy đúng một lần ở P4.
4. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
5. Không commit/push cho đến khi user yêu cầu.
6. **Test mới phải ĐỎ trước.** Viết test → chạy → thấy đỏ vì đúng lý do → mới sửa nguồn.
   Test xanh ngay lần đầu = test không khoá gì, phải viết lại.
7. **CẤM sửa chữ của luật.** Chỉ được thêm dòng link, thêm khối mục lục, sửa mã công cụ.
   Cuối mỗi task chạm `skills/`: soi `git diff` xác nhận không dòng luật nào đổi chữ.
8. **CẤM sửa tay `portable_claude/` và `portable_codex/`** — chỉ sinh bằng `build_portable.py`.

## P1 — Khoá hành vi trước khi sửa (test đỏ)
- Dùng: `tdq-spec`, `tdq-plan`, `tdq-build`
  - Nạp: tdq-spec/tdq-plan đã dùng để viết spec+plan này; tdq-build nạp ở đầu phase implement.
  - Để: chạy trọn plan trong một turn, đúng luật tick và red→green.
  - Ra: 10 đầu ra §2 của spec.
  - Kiểm: mọi task trong plan này tick `[x]` và full suite xanh.
  - Không dùng cho: đổi phạm vi spec — phạm vi đã chốt ở cổng duyệt spec.
- Dùng: `scripts/skill_tokens.py`
  - Nạp: T2.1 (sửa nó) và T4.1 (đo lại sau khi sửa).
  - Để: đếm token thân + reference bằng tokenizer thật, đủ cả thư mục con.
  - Ra: số trước/sau trong report, cùng một cách đếm.
  - Kiểm: `python3 scripts/skill_tokens.py --theo-phase` liệt kê 35 file reference.
  - Không dùng cho: đo mô tả skill — đó là việc của hướng D, đã đóng.
- Dùng: `scripts/build_portable.py`
  - Nạp: T3.1, sau khi `skills/` đã sửa xong.
  - Để: sinh lại hai bản portable từ một nguồn.
  - Ra: `portable_claude/`, `portable_codex/` kèm `manifest.json` khớp sha256.
  - Kiểm: lệnh exit 0, bộ test portable xanh.
  - Không dùng cho: sửa nội dung skill — nó chỉ sao chép và thay biến.

- [x] **T1.1** (n4) Viết test khoá luật một tầng: dựng đồ thị link `.md` trong `skills/`
  (giải cả link tương đối cùng thư mục), khẳng định mọi file `references/**/*.md` được ít
  nhất một `SKILL.md` trỏ thẳng — Test: chạy trên cây hiện tại phải ĐỎ và liệt kê đúng 14
  file ở tầng ≥ 2
  - Chạm: `tests/test_reference_mot_tang.py`
- [x] **T1.2** (n3) Nối vào cùng file test: mọi link `.md` trong `skills/` phải trỏ tới
  file có thật (không link chết) — Test: xanh ngay trên cây hiện tại (đây là test hồi
  quy, khoá để bước sửa link không tạo link hư)
  - Chạm: `tests/test_reference_mot_tang.py`
  - Cần: T1.1
- [x] **T1.3** (n3) Nối vào cùng file test: file reference > 100 dòng phải có `## Mục lục`
  liệt kê đủ các tiêu đề `##` của chính nó — Test: chạy trên cây hiện tại phải ĐỎ và liệt
  kê đúng 8 file
  - Chạm: `tests/test_reference_mot_tang.py`
  - Cần: T1.1

## P2 — Sửa nguồn (hai nhánh song song)

### Nhánh A — cấu trúc link + mục lục (M1)
- [x] **T2A.1** (n5) Thêm dòng trỏ thẳng ở `SKILL.md` cho 14 file đang ở tầng ≥ 2:
  `tdq-build/SKILL.md` → `rules/index.md`; `tdq-conventions/SKILL.md` →
  `measure-scenario.md`, `plugin-routing.md`; `tdq-intake/SKILL.md` → `issue-triage.md`,
  `skill-inventory.md`. Trong `rules/index.md` bảo đảm có link tới đủ 10 file ngôn ngữ —
  Test: test T1.1 chuyển từ đỏ sang XANH
  - Chạm: `skills/tdq-build/SKILL.md`, `skills/tdq-conventions/SKILL.md`,
    `skills/tdq-intake/SKILL.md`, `skills/tdq-build/references/rules/index.md`
  - Cần: T1.1
- [x] **T2A.2** (n4) Thêm `## Mục lục` cho 8 file reference > 100 dòng (`quick-lane`,
  `plan-template`, `spec-template`, `team-mode`, `user-facing-block`, `scope-round`,
  `clean-code`, `qc`) — Test: test T1.3 chuyển từ đỏ sang XANH
  - Chạm: 8 file trong `skills/*/references/`
  - Cần: T1.3
- [x] **T2A.3** (n2) Soi `git diff -- skills/` xác nhận chỉ có dòng link và khối mục lục,
  không dòng luật nào đổi chữ — Test: `git diff -- skills/` không có dòng `-` nào ngoài
  các dòng bị thay bởi chính link/mục lục; ghi kết quả vào mục QC file này
  - Chạm: (chỉ đọc)
  - Cần: T2A.1, T2A.2

### Nhánh B — công cụ đo (M2)
- [x] **T2B.1** (n3) Viết test khoá `skill_tokens.py` không sót thư mục con: dựng cây skill
  giả có `references/sub/x.md`, khẳng định file đó được đếm — Test: chạy với bản
  `skill_tokens.py` hiện tại phải ĐỎ
  - Chạm: `tests/test_skill_tokens.py`
- [x] **T2B.2** (n2) Sửa `skill_tokens.py` dòng 138 sang glob đệ quy — Test: T2B.1 XANH;
  `--theo-phase` liệt kê 35 file reference (thay vì 25) và trần ≥ 89.000 token
  - Chạm: `scripts/skill_tokens.py`
  - Cần: T2B.1

## P3 — Sinh lại portable (M3)
- [x] **T3.1** (n3) Nối test vào bộ test portable: mọi file `references/**/*.md` của
  `skills/` phải có mặt ở cả `portable_claude/` lẫn `portable_codex/` — Test: xoá thử một
  file reference khỏi bản sinh thì test ĐỎ
  - Chạm: `tests/test_build_portable.py`
  - Cần: T2A.3
- [x] **T3.2** (n2) Chạy `python3 scripts/build_portable.py` sinh lại hai bản — Test: lệnh
  exit 0; bộ test portable và test tự kiểm máy đích đều xanh; `manifest.json` khớp sha256
  file thật
  - Chạm: `portable_claude/`, `portable_codex/`
  - Cần: T3.1

## P4 — Đo lại, đính chính, report (M4)
- [x] **T4.1** (n3) Đo lại bằng bản `skill_tokens.py` mới: trần đủ file, thân 5 skill,
  và tổng reference THẬT mở của một request lane full — Test: ba số có mặt trong report,
  mỗi số kèm lệnh sinh ra nó
  - Chạm: (chỉ đo)
  - Cần: T2B.2, T2A.3
- [x] **T4.2** (n1) Chạy full suite đúng một lần — Test: toàn bộ test suite của repo xanh
  - Chạm: (chỉ chạy)
  - Cần: T3.2, T4.1
- [x] **T4.3** (n3) Thêm mục "Đính chính hướng C 2026-08-19" vào đề án: số 55.719 thiếu
  14.554 token của `rules/`, và tiền đề "tách sâu thêm" đi ngược hướng dẫn chính thức —
  Test: `grep -c "Đính chính hướng C 2026-08-19"` ≥ 1, mục 3 cũ còn nguyên, `doc_lint` exit 0
  - Chạm: `docs/tdq/audit/de-an-toi-uu-context.md`
  - Cần: T4.1
- [x] **T4.4** (n3) Viết report: tách rõ phần "đổi gì về chất lượng (tầng luật)" và phần
  "đổi gì về token", ghi số trước/sau CÙNG một cách đếm mới — Test: `doc_lint` exit 0
  - Chạm: `docs/tdq/reports/2026-08-19-0121-huong-c-nap-reference.md`
  - Cần: T4.2, T4.3

**Xong P4 khi**: 10 đầu ra §2 tồn tại, full suite xanh, `doc_lint` exit 0.

## Cụm song song

Hai cụm chạy song song được sau khi P1 xong:

| Cụm | Task | Vùng file | Vì sao tách được |
|---|---|---|---|
| A — cấu trúc link | T1.1, T1.3, T2A.1, T2A.2, T2A.3 | `skills/`, `tests/test_reference_mot_tang.py` | chỉ chạm markdown trong `skills/` |
| B — công cụ đo | T2B.1, T2B.2 | `scripts/skill_tokens.py`, `tests/test_skill_tokens.py` | chỉ chạm mã Python, không đụng `skills/` |

Hai cụm không dùng chung file nào. P3 và P4 phải đợi CẢ hai cụm xong (P3 cần nguồn đã sửa,
P4 cần công cụ đo đã sửa để đo nguồn đã sửa).

## QC

| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q1 | Luật một tầng | PASS | test một tầng xanh; 14 file trước đó ở tầng ≥ 2 nay được `SKILL.md` trỏ thẳng; ngoại lệ `rules/` có test riêng bắt cửa vào ở tầng 1 và trỏ đủ 9 file anh em |
| Q2 | Không link chết | PASS | test link chết xanh trên toàn bộ `skills/` |
| Q3 | Công cụ đo đếm đủ | PASS | `skill_tokens.py --theo-phase` báo 35 file reference (trước: 25), trần 90.999 ≥ 89.000 |
| Q4 | Mục lục | PASS | 8 file > 100 dòng đều có `## Mục lục` khớp đủ tiêu đề `##` của chính nó |
| Q5 | Nội dung luật không đổi | PASS | 329/329 điểm neo `luat-hien-co.md` còn nguyên; kiểm bằng máy: 10 dòng bị xoá đều có bản thay tương đương sau khi gỡ cú pháp link → 0 dòng mất chữ |
| Q6 | Portable đồng bộ | PASS | `build_portable.py` exit 0; 67 test portable + tự kiểm máy đích xanh; test mới bắt đủ reference ở cả hai bản |
| Q7 | Test khoá thật sự khoá | PASS | 3 lưới đều ĐỎ trước khi sửa; lưới portable chứng minh bằng giấu tạm `rules/python.md` khỏi bản codex → đỏ, trả lại → xanh |
| Q8 | Full suite | PASS có điều kiện | 1.006 pass / 1.215 subtest pass; 25 subtest đỏ đều nằm trong `tests/test_skill_router.py` (skill `figma-*`, `datarobot-*`) — lỗi CÓ SẴN, chứng minh bằng `git stash` toàn bộ thay đổi rồi chạy lại vẫn đúng 25 đỏ |
| Q9 | Số trước/sau cùng cách đếm | PASS | bảng trước/sau trong report đo bằng cùng một hàm đếm, cùng danh sách 37 file |

Hai việc phát sinh đã xử lý ngay, không cần duyệt lại (quy tắc 4): nới trần dòng
`tdq-conventions` 143 → 145 có ghi lý do tại chỗ; cập nhật 104 số dòng lệch trong
`luat-hien-co.md` bằng cách dò chữ neo.
