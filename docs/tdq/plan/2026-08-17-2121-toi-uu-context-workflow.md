# PLAN — Đo và đề án tối ưu context cho bộ workflow TDQ

Ngày: 2026-08-17 · Spec: ../spec/2026-08-17-2121-toi-uu-context-workflow.md (bản 1.2, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — 20 task nhưng chỉ 5 nhóm file rời nhau, phần lớn task chồng lên `skill_tokens.py` và file đề án; benchmark request trước cho ngưỡng hoàn vốn của mode đội là 40% task tách được, plan này chỉ đạt ~25%. (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH · mode main

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. **Cấm ghi vào bất kỳ file settings nào** (`~/.claude/settings.json`,
   `.claude/settings*.json`) và cấm sửa file trong `skills/`, `portable_claude/`,
   `portable_codex/`. Đây là ranh giới spec §5, Q9 và Q14 khoá lại.

## P1 — Thước đo token

- [x] **T1.1** (n2 e8m) Dựng venv `.venv-tokens/` cài `anthropic-tokenizer==0.1.0`, thêm vào `.gitignore` — Test: `.venv-tokens/bin/python -c "import anthropic_tokenizer"` exit 0 và `git status --short` không thấy `.venv-tokens`
  - Chạm: `.gitignore` → file sẵn có, không node nào phụ thuộc
- [x] **T1.2** (n6 e25m) Viết `scripts/skill_tokens.py`: lõi đếm token + lệnh `--theo-phase` in bảng token 6 khối phase, lỗi rõ ràng khi thiếu thư viện — Test: `python3 scripts/skill_tokens.py --theo-phase` exit 0 in đủ 6 khối; gỡ thư viện → exit khác 0, stderr nêu cách cài, KHÔNG in bảng
  - Chạm: `scripts/skill_tokens.py` → file mới, chưa node nào phụ thuộc
- [x] **T1.3** (n5 e20m) Thêm lệnh `--mo-ta` vào `skill_tokens.py`: đo token mô tả mọi skill ĐANG BẬT, phân theo nguồn và theo mục (workflow · code · design · web · dữ liệu · game engine · khác) — Test: `python3 scripts/skill_tokens.py --mo-ta` in bảng có cột token và cột mục; số skill bằng đúng số của `python3 scripts/skill_inventory.py --tat-ca`
  - Chạm: `scripts/skill_tokens.py` → sau `T1.2`, cùng file
- [x] **T1.4** (n4 e18m) Viết `tests/test_skill_tokens.py` phủ: thiếu thư viện, phân mục, tổng khớp inventory — Test: `python3 -m pytest tests/test_skill_tokens.py -q` xanh, ≥ 6 test
  - Chạm: `tests/test_skill_tokens.py` → file mới, chưa node nào phụ thuộc

**Xong P1 khi**: `--theo-phase` và `--mo-ta` cùng exit 0, `pytest tests/test_skill_tokens.py` xanh.

## P2 — Kho tra cứu skill và nguyên mẫu router

- [x] **T2.1** (n4 e15m) Sinh `docs/tdq/audit/skill-index.json` từ `skill_inventory.py`, mỗi bản ghi đủ 4 trường `ten`/`mo_ta`/`nguon`/`duong_dan` — Test: `python3 -c` đếm bản ghi bằng số skill của `skill_inventory.py --tat-ca`; mọi `duong_dan` mở được
  - Chạm: `docs/tdq/audit/skill-index.json` → file mới, chưa node nào phụ thuộc
- [x] **T2.2** (n7 e30m) Viết `scripts/skill_router.py`: BM25 offline trên kho, lệnh `--tra "<câu>"` in top-k kèm điểm — Test: ngắt biến API key rồi `python3 scripts/skill_router.py --tra "sửa lỗi unity shader"` exit 0, in top-k, không gọi mạng
  - Chạm: `scripts/skill_router.py` → file mới, chưa node nào phụ thuộc
- [x] **T2.3** (n6 e28m) Viết `tests/test_skill_router.py` với ≥ 20 prompt mẫu, mỗi prompt ghi sẵn skill ĐÚNG phải ra; tính tỉ lệ trúng top-1 và top-5 — Test: `python3 -m pytest tests/test_skill_router.py -q` xanh và in ra hai tỉ lệ bằng số thật
  - Chạm: `tests/test_skill_router.py` → file mới, chưa node nào phụ thuộc

**Xong P2 khi**: router chạy offline được và hai tỉ lệ trúng đã có số.

## P3 — Trích luật và test khoá luật

- [x] **T3.1** (n7 e35m) Viết `docs/tdq/audit/luat-hien-co.md`: mỗi luật một dòng, mã `L###`, trỏ `file:dòng` nguồn — Test: `grep -c "^| L" docs/tdq/audit/luat-hien-co.md` ra số ≥ số dòng mệnh lệnh `doc_lint` đếm được; soi 5 dòng bất kỳ đều mở được đúng chỗ
  - Dùng: `tdq-conventions`
  - Để: lấy đúng danh mục luật gốc cần trích (working log, failover, định tuyến plugin, QC), nạp skill TRƯỚC bước đỏ. Agent ngoài không có skill system: đọc `skills/tdq-conventions/SKILL.md` rồi làm theo.
  - Ra: `docs/tdq/audit/luat-hien-co.md`
  - Kiểm: `python3 scripts/doc_lint.py docs/tdq/audit/luat-hien-co.md` exit 0
  - Không dùng cho: sửa chính file skill `tdq-conventions` — request này chỉ đọc
- [x] **T3.2** (n7 e35m) Viết `tests/test_luat_skill.py` khoá từng luật của `luat-hien-co.md` — Test: xoá một luật khỏi BẢN SAO skill trong thư mục tạm → test đỏ đúng luật đó; nguyên bản → xanh
  - Chạm: `tests/test_luat_skill.py` → file mới, chưa node nào phụ thuộc

**Xong P3 khi**: mọi luật trích ra đều trỏ được nguồn và test khoá chứng minh đỏ-trước-xanh-sau.

## P4 — Đo thực nghiệm và xác nhận giả định

- [x] **T4.1** (n3 e12m) Đối chiếu ba bản `skills/`, `portable_claude/`, `portable_codex/`, liệt kê mọi file lệch — Test: mục đối chiếu có bảng file lệch, hoặc ghi rõ "không lệch"; `git status --short skills portable_claude portable_codex` rỗng
- [x] **T4.2** (n5 e25m) Dịch thử ĐÚNG MỘT file skill sang tiếng Anh trong thư mục tạm, đo token trước/sau bằng `skill_tokens.py`, ghi hệ số đo được — Test: mục báo cáo có token trước, token sau, tên file; file gốc trong `skills/` không đổi một byte
- [x] **T4.3** (n4 e18m) Sinh `docs/tdq/audit/skill-overrides-de-xuat.json` — mặc định `name-only`, chỉ `off` cho nhóm chắc chắn lạc mục — Test: `python3 -c "import json;json.load(...)"` exit 0; 100% khoá có trong inventory; 100% giá trị thuộc 3 mức hợp lệ; `md5` của `~/.claude/settings.json` trước/sau không đổi
  - Chạm: `docs/tdq/audit/skill-overrides-de-xuat.json` → file mới, chưa node nào phụ thuộc
- [ ] **T4.4** (n5 e20m) Chạy THẬT một lượt xác nhận skill ở mức `name-only` có còn gọi được không, dán output — Test: mục báo cáo có output thật; nếu KHÔNG gọi được thì kiến trúc 3 tầng phải đổi ngay trong `T5.3`
  - **KHÔNG LÀM ĐƯỢC — để trống `[ ]` có chủ ý.** Test đòi "output thật", và request
    này không tạo ra được output thật: quy tắc 7 cấm ghi settings, mà `skillOverrides`
    chỉ đọc lúc mở phiên nên có ghi cũng không quan sát được trong turn. Đã tick `[x]`
    một lần rồi trả lại `[ ]` sau khi QC độc lập chỉ ra là tick sai — bằng chứng gián
    tiếp không phải là output thật. Thay thế: `docs/tdq/audit/do-thuc-nghiem.md` §4 ghi
    bằng chứng chuỗi binary + cách user tự xác nhận trong 1 phút, và `T5.3` đã viết để
    đứng vững với cả hai kết quả.

**Xong P4 khi**: bốn số thực nghiệm (lệch bản, hệ số dịch, file đề xuất, `name-only`) đều có bằng chứng chạy.

## P5 — Báo cáo đề án

- [x] **T5.1** (n6 e30m) Viết `docs/tdq/audit/de-an-toi-uu-context.md`: khung + hướng A/B/C kèm token tiết kiệm, rủi ro, thứ tự làm — Test: `python3 scripts/doc_lint.py` exit 0; có kết luận "tối ưu được / không" kèm số
  - Chạm: `docs/tdq/audit/de-an-toi-uu-context.md` → file mới, chưa node nào phụ thuộc
- [x] **T5.2** (n4 e18m) Thêm mục hướng D vào đề án: bảng 3 kịch bản (giữ nguyên · `name-only` · `off`) kèm token còn lại và giới hạn của `skillOverrides` — Test: mục có đủ 3 dòng kịch bản và dòng nêu giới hạn cấu hình tĩnh
  - Chạm: `docs/tdq/audit/de-an-toi-uu-context.md` → sau `T5.1`, cùng file
- [x] **T5.3** (n5 e22m) Thêm mục hướng E: bảng token 4 kiến trúc, tỉ lệ trúng đo ở `T2.3`, lỗ hổng "model phải nhớ đi tra" và cách bịt bằng hook `UserPromptSubmit` — Test: mục có đủ 4 dòng kiến trúc, hai tỉ lệ trúng bằng số; tỉ lệ top-5 dưới 90% thì phải có câu khuyến nghị KHÔNG chuyển sang router
  - Chạm: `docs/tdq/audit/de-an-toi-uu-context.md` → sau `T5.2`, cùng file
- [x] **T5.4** (n3 e12m) Ghi một fact vào mem0 về hệ số token Việt/Anh đo được — Test: `search_memories` với project `TDQWorkflow` trả về đúng fact vừa ghi
  - Dùng: `mem0-memory` (mcp)
  - Để: lưu hệ số Việt/Anh đo thật ở `T4.2` để request tối ưu sau không phải đo lại, nạp skill TRƯỚC bước đỏ. Agent ngoài không có skill system: đọc `skills/mem0-memory/SKILL.md` rồi làm theo.
  - Ra: một bản ghi mem0 project `TDQWorkflow` chứa hệ số đo được
  - Kiểm: gọi `search_memories` project `TDQWorkflow`, kết quả có hệ số vừa ghi
  - Không dùng cho: ghi nội dung skill, số token thô, hay bất cứ thứ gì đã nằm trong repo

**Xong P5 khi**: đề án có đủ năm hướng kèm số và thứ tự nên làm.

## P6 — Log & test bắt buộc

- [x] **T6.1** (n3 e12m) Log service cho cả `skill_tokens.py` và `skill_router.py`: timestamp ISO + tên lệnh + tham số ra stderr, tắt bằng `TDQ_LOG=0` — Test: chạy 1 lệnh mỗi script có và không `TDQ_LOG=0`; stderr có dòng ISO khi bật, rỗng khi tắt
  - Chạm: `scripts/skill_tokens.py`, `scripts/skill_router.py` → sau `T1.3` và `T2.2`
- [x] **T6.2** (n2 e10m) Chạy full suite đúng một lần và ghi số — Test: `python3 -m pytest tests/ -q` xanh, số test ≥ 874

**Xong P6 khi**: log service chứng minh bật/tắt được và full suite xanh.

## P7 — QC

Chạy đủ 19 hạng mục §6 của spec, ghi bằng chứng vào `docs/tdq/qc/<slug>.md`.

- [x] **T7.1** (n5 e25m) Chạy Q1–Q18 và ghi bằng chứng thật vào file qc — Test: file qc có đủ 18 dòng, mỗi dòng kèm output chép từ terminal
- [x] **T7.2** (n4 e20m) QC độc lập bằng agent — Test: có verdict PASS/FAIL kèm output agent tự chạy
  - Dùng: `tdq-qc-tester`
  - Để: chấm lại Q1–Q18 độc lập, không đọc file qc do tôi viết, nạp skill TRƯỚC bước đỏ. Agent ngoài không có skill system: đọc `skills/tdq-qc-tester/SKILL.md` rồi làm theo.
  - Ra: mục `## QC độc lập` trong `docs/tdq/qc/2026-08-17-2121-toi-uu-context-workflow.md`
  - Kiểm: mục đó có verdict và ít nhất 5 số agent tự chạy ra
  - Không dùng cho: tự sửa code hay tài liệu — agent chỉ chấm, vòng fix do tôi làm

**Xong P7 khi**: 19 hạng mục PASS, trần 3 vòng fix chưa vượt.

## Definition of Done

Trỏ về §6 của spec — 19 hạng mục:

| # | Hạng mục | Lệnh kiểm |
|---|---|---|
| Q1 | Test suite không đỏ | `python3 -m pytest tests/ -q` (≥ 874) |
| Q2 | Thước đo chạy được | `python3 scripts/skill_tokens.py --theo-phase` |
| Q3 | Cấm đoán token | gỡ thư viện khỏi venv rồi chạy lại |
| Q4 | Luật trích có nguồn | `grep -c "^| L" docs/tdq/audit/luat-hien-co.md` |
| Q5 | Test khoá luật thật sự khoá | xoá 1 luật khỏi bản sao rồi chạy test |
| Q6 | Ba bản không lệch ngầm | mục đối chiếu trong đề án |
| Q7 | Hệ số Việt/Anh là số ĐO | mục bản dịch thử trong đề án |
| Q8 | Đề án trả lời đúng câu user hỏi | đọc `de-an-toi-uu-context.md` |
| Q9 | Không sửa skill | `git status --short skills portable_claude portable_codex` |
| Q10 | Log service | chạy 1 lệnh có và không `TDQ_LOG=0` |
| Q11 | doc_lint | `python3 scripts/doc_lint.py` trên file audit |
| Q12 | Đo mô tả skill khớp inventory | `skill_tokens.py --mo-ta` so `skill_inventory.py --tat-ca` |
| Q13 | File `skillOverrides` đề xuất hợp lệ | `python3 -c "import json;json.load(...)"` + đối chiếu inventory |
| Q14 | Không đụng settings của user | `md5` của `~/.claude/settings.json` trước/sau |
| Q15 | Kho tra cứu khớp inventory | đếm bản ghi `skill-index.json` |
| Q16 | Router chạy offline | `skill_router.py --tra "..."` khi không có API key |
| Q17 | Tỉ lệ trúng có số | `python3 -m pytest tests/test_skill_router.py -q` |
| Q18 | Router chưa lắp vào luồng | `grep -r "skill_router" .claude/settings*.json hooks/` |
| Q19 | QC độc lập | agent `tdq-qc-tester` chạy lại Q1–Q18 |
