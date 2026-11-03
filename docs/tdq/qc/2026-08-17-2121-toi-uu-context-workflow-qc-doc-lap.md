# QC độc lập (agent tdq-qc-tester) — 2026-08-17-2121-toi-uu-context-workflow

Tất cả lệnh dưới đây tự chạy lại, không đọc file qc do agent build viết trước.

## Q1 — pytest tests/ -q
```
913 passed, 1189 subtests passed in 81.42s
```
≥ 874 → PASS.

## Q2 — skill_tokens.py --theo-phase
Exit 0, in đủ 6 khối: luôn nạp/intake/spec/plan/build/luật kèm, trần 70.924 token. PASS.

## Q3 — cấm đoán token
`TDQ_TOKENS_VENV=/nonexistent/python python3 scripts/skill_tokens.py --theo-phase`
→ exit 3, stderr "thiếu thư viện đếm token ... CẤM ước lượng ký tự/4", KHÔNG in bảng. PASS.
(Dùng cờ `TDQ_TOKENS_VENV` sẵn có trong script để giả lập thiếu venv mà không đụng venv thật.)

## Q4 — luật có nguồn
`grep -c "^| L" docs/tdq/audit/luat-hien-co.md` = 329.
Soi 8 dòng random (seed cố định, khác 5 dòng agent build đã soi):
L018, L174, L032, L024, L263, L068, L282, L101 — tất cả 8/8 mở đúng `file:dòng`, nội dung khớp. PASS.

## Q5 — test khoá luật
Tự dựng lại phép thử độc lập (không dùng lại `LuoiBatDuocMatLuatTest` có sẵn): copy
`skills/tdq-build/references/qc.md` ra tempdir, xoá đúng dòng mang L018, chạy lại hàm
đối chiếu `luat_con_khong` cho TOÀN BỘ 329 luật (327 luật khác trỏ file gốc, L018 trỏ
bản đã xoá) → chỉ đúng L018 báo mất, 328 luật còn lại xanh. File gốc trong `skills/`
không đổi (đã kiểm bằng đọc lại). `git status --short skills portable_claude
portable_codex` rỗng. PASS.

## Q6 — ba bản không lệch ngầm
Tự viết script diff md5+nội dung độc lập (Python thuần, không dùng lại logic report).
`skills` vs `portable_claude`: common 44, diff byte 15, diff nội dung 0 — khớp báo cáo.
`skills` vs `portable_codex`: common 44, diff byte 15, **diff nội dung 15 nếu chỉ chuẩn
hoá 2 pattern đường dẫn mà do-thuc-nghiem.md §1 mô tả** (`${CLAUDE_PLUGIN_ROOT}/scripts/`
và `${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/`). portable_codex thực tế dùng pattern
thứ ba `./scripts/` — KHÔNG có trong mô tả phương pháp. Thêm pattern này vào thì diff
nội dung mới về 0, khớp con số cuối cùng "0" mà báo cáo ghi.
→ Số cuối (0 file lệch nội dung) TÁI LẬP ĐƯỢC, nhưng phương pháp mô tả trong
do-thuc-nghiem.md §1 là THIẾU (chỉ nêu 2/3 pattern cần chuẩn hoá) — xem DEFECT #1.
PASS (số đúng), kèm 1 defect tài liệu.

## Q7 — hệ số Việt/Anh
`md5 skills/tdq-conventions/references/approval.md` = `c890b7e70e33a3ef967a78421ce506d1`
— khớp báo cáo. `wc -m` = 1795 ký tự — khớp. `.venv-tokens/bin/python -c
"anthropic_tokenizer.count_tokens(...)"` = 1070 token — khớp chính xác con số trước
(1.070). Bản dịch tiếng Anh không còn trong repo (đúng thiết kế: dịch trong thư mục
tạm, không giữ lại) nên không tái lập được số "668" và "0,624" một cách độc lập —
chấp nhận vì file gốc khớp 100% và quy trình (xoá bản dịch, giữ file gốc nguyên) đúng
như spec yêu cầu. PASS có điều kiện.

## Q8 — báo cáo trả lời đúng câu hỏi
`de-an-toi-uu-context.md` §0 có kết luận rõ "Tối ưu được, và biên độ lớn hơn ước
lượng ban đầu" kèm bảng số; §6 xếp thứ tự 5 hướng (D, C, B, A, E-dừng). PASS.

## Q9 — không sửa skill
`git status --short skills portable_claude portable_codex` → rỗng. PASS.

## Q10 — log service
`python3 scripts/skill_tokens.py --theo-phase` (mặc định) → stderr có 2 dòng
`[2026-08-17T22:57:53+07:00] ...`. `TDQ_LOG=0 python3 scripts/skill_tokens.py
--theo-phase` → stderr 0 byte. Lặp lại y hệt cho `skill_router.py --tra "test"`.
Cả 2 script đều đúng hành vi. PASS.

## Q11 — doc_lint
`python3 scripts/doc_lint.py docs/tdq/audit/luat-hien-co.md
docs/tdq/audit/de-an-toi-uu-context.md docs/tdq/audit/do-thuc-nghiem.md` → exit 0. PASS.

## Q12 — mô tả khớp inventory
`skill_tokens.py --mo-ta` → "Tổng: 284 skill đang bật · 29.072 token mô tả · 3.208
token nếu chỉ giữ tên". `skill_inventory.inventory('.')` (gọi trực tiếp Python) → 284.
Khớp. Bảng có cột token và cột mục (7 mục). Đã TỰ TÍNH LẠI độc lập con số hướng D
(29.072 → 3.629, tiết kiệm 87,5%) từ chính bảng theo-nguồn của `--mo-ta`: cộng
token-nếu-giữ-tên của nhóm `dữ liệu+web+khác+code` (220 skill) = 2.451, cộng
token-mô-tả của `design+game engine` (41 skill, đặt `off`) = 0, cộng token-mô-tả của
`workflow` (23 skill, giữ nguyên) = 1.178 → tổng 3.629. KHỚP CHÍNH XÁC số trong cả
`de-an-toi-uu-context.md` và `do-thuc-nghiem.md` — hai file audit dùng CÙNG một cách
đo, không đá nhau. PASS.

## Q13 — skillOverrides hợp lệ
`json.load(...)` OK, 261 khoá, giá trị ∈ {name-only(220), off(41)}, 0 khoá lạ, 0 giá
trị sai. 100% khoá có thật trong inventory (đối chiếu trực tiếp bằng Python). PASS.

## Q14 — không đụng settings user
`md5 ~/.claude/settings.json` = `a6867f29f5a38c3dc51d048a0cd81471` — khớp chính xác
số khoá trong spec/QC. PASS.

## Q15 — kho tra cứu khớp inventory
Số bản ghi `skill-index.json` = 284 = inventory 284 → khớp. NHƯNG kiểm "mọi duong_dan
mở được": phát hiện **10/284 bản ghi có `duong_dan` RỖNG** (không phải sai đường dẫn,
mà là chuỗi rỗng `""`), gồm: `unity-mcp-orchestrator`,
`"adobe-batch-edit-photos"` (tên còn dính dấu ngoặc kép literal — dấu hiệu bug parse
frontmatter), 6 skill nhóm `canva-*`, `firecrawl`, `writing-hookify-rules`.
→ **FAIL** — trái điều kiện PASS của spec Q15 ("mọi duong_dan mở được") và trái tuyên
bố "0 đường dẫn hỏng" trong file qc cũ. Xem DEFECT #2.

## Q16 — router offline
`env -u ANTHROPIC_API_KEY -u TAVILY_API_KEY -u OPENAI_API_KEY python3
scripts/skill_router.py --tra "sửa lỗi unity shader"` → exit 0, top-1
`unity-shadergraph-design` 13.26. Đọc source: không `import requests/urllib/http`.
PASS.

## Q17 — tỉ lệ trúng có số
`python3 -m pytest tests/test_skill_router.py -q -s` →
"TỈ LỆ TRÚNG trên 22 prompt mẫu: top-1 = 27.3% · top-5 = 45.5%" — khớp chính xác số
ghi trong đề án, ≥ 20 prompt (22). Đọc bộ prompt mẫu: có luật chống nới đáp án (mỗi
tuple ≥2 tên phải trích mô tả thật trong comment), có nhóm khó với tỉ lệ trúng 0% —
không có dấu hiệu làm dễ cho đẹp số. PASS.

## Q18 — router chưa lắp hook
`grep -r "skill_router" .claude/settings*.json hooks/` → không khớp (exit 1). Kiểm
thêm cả `portable_claude/`, `portable_codex/` (settings + hooks.json) → cũng không
khớp dòng nào. PASS.

## Q19 — QC độc lập
Chính báo cáo này.

---

## DEFECTS

1. **NHẸ — do-thuc-nghiem.md §1 mô tả phương pháp chuẩn hoá đường dẫn thiếu 1
   pattern.** Văn bản chỉ nêu 2 pattern (`${CLAUDE_PLUGIN_ROOT}/scripts/` và
   `${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/`) nhưng `portable_codex` thực tế dùng
   `./scripts/` — thiếu pattern này thì diff nội dung giữa `skills/` và
   `portable_codex` ra 15, không phải 0 như báo cáo. Số cuối "0" đúng và tái lập được
   nếu thêm đúng pattern, nhưng ai đọc văn bản để tái lập sẽ ra sai số. — nghi ở:
   `docs/tdq/audit/do-thuc-nghiem.md:12-14`

2. **VỪA — `skill-index.json` có 10/284 bản ghi `duong_dan` rỗng, trái điều kiện PASS
   của Q15 và trái tuyên bố "0 đường dẫn hỏng" trong QC trước.** Một trong 10 tên còn
   dính nguyên dấu ngoặc kép literal (`"adobe-batch-edit-photos"`), gợi ý lỗi parse
   frontmatter/tên skill ở bước sinh `skill-index.json` (nghi hàm dựng đường dẫn không
   xử lý được các skill dạng canva-*, firecrawl, hookify, unity-mcp-orchestrator —
   khả năng do các skill này định nghĩa nhiều "skill ảo" trong cùng 1 SKILL.md, nên
   logic 1-skill-1-thư-mục không tìm ra file). Router vẫn trả các skill này về được
   (đã thấy `unity-mcp-orchestrator` ở #3 top-k của Q16) nên KHÔNG chặn Q16/Q17, nhưng
   vi phạm rõ điều kiện PASS đã ghi trong spec §6 dòng Q15 và đầu ra #10 (§2). — nghi
   ở: script sinh `docs/tdq/audit/skill-index.json` (không thấy script generator được
   commit trong `scripts/`, nghi việc sinh file này không lặp lại được bằng lệnh cố
   định — thiếu tính tái lập).

3. **NHẸ — T4.4 trong plan bị tick `[x]` dù chưa đạt Test criterion tự đặt.** Task
   ghi "Test: mục báo cáo có output thật" nhưng report thừa nhận "CHƯA đo được", chỉ
   đưa bằng chứng gián tiếp (chuỗi trong binary). Minh bạch, có giải thích hợp lý
   (bị chặn bởi chính ràng buộc Q14/plan §7), nhưng theo đúng nghĩa đen thì task
   không thoả điều kiện xong của chính nó — không phải lỗi che giấu, nhưng đáng lẽ
   phải để `[~]` hoặc note rõ trong DoD thay vì tick xong. — nghi ở:
   `docs/tdq/plan/2026-08-17-2121-toi-uu-context-workflow.md:63`,
   `docs/tdq/audit/do-thuc-nghiem.md:73-91` (mục 4).

VERDICT: FAIL: Q15 (10/284 duong_dan rỗng, trái điều kiện PASS spec). Các hạng mục
còn lại Q1-Q14, Q16-Q19 đều PASS với bằng chứng tự chạy độc lập ở trên.
