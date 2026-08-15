# REPORT — Tối ưu thời gian xử lý các phase của workflow (`2026-08-15-toi-uu-thoi-gian-phase` · lane full · mode main · 18 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 chốt mốc đo trước · P2 đưa luật gộp tool call vào thân `tdq-conventions/SKILL.md`
§10 với nhãn **tầng 2 — runtime** (trần dòng skill nới 120→130), tách `context-budget.md`
thành chi phí bước / chi phí context, thêm bảng **Cấm gộp** 4 ca và **5 ca BẮT BUỘC đọc lại**,
thêm mục "Xếp luật vào tầng nào" vào `soul.md` (chỉ THÊM), đồng bộ `portable/AGENTS.md` ·
P3 viết `scripts/step_audit.py` + transcript mẫu, sửa `token_audit.py` suy sai đường dẫn khi
tên project có gạch dưới · P4 `tests/test_step_budget.py` 12 test · P5 mốc sau + CHANGELOG 0.19.0.

**Kết quả:** luật đọc lại là luật MỀM đúng yêu cầu user — chuỗi "cấm đọc lại" 0 lần, có câu
chốt "Nghi ngờ thì đọc lại: chất lượng đứng trên runtime" ở cả skill lẫn bản portable ·
chỉ số đích **tool call trên mỗi lượt**: Heineken 1,03 (3.085 lượt) → phiên build này 1,07
(2.363 lượt), CHƯA cải thiện vì luật mới nằm trong SKILL.md nên chỉ có hiệu lực từ phiên sau —
phép đo thật phải chạy lại `step_audit.py` sau một request đầy đủ ở phiên mới · phần thêm vào
thân skill 444 ký tự (trần 900) nên chi phí context mỗi turn gần như không đổi.

**Đính chính số đo:** con số "1,00 tool call mỗi lượt / 4.809 bước" ở phase analyze là ảo —
Claude Code tách một câu trả lời thành nhiều bản ghi jsonl và chép `usage` vào từng bản, đếm
theo bản ghi thì luôn ra 1,00 và số bước bị thổi phồng. Đo lại bằng `step_audit.py` (gom theo
`requestId`): 3.234 bước · 1,03 tool call mỗi lượt. Hướng kết luận không đổi (~97% số lượt chỉ
phát một tool call). Đã đính chính trong `brief` và mục `## Mốc trước` của file QC.

**Kiểm:** `python3 -m pytest -q` → **608 passed, 306 subtests** (trước request 596) ·
`doc_lint.py` 10 file exit 0 · `git diff soul.md` 19 thêm / **0 xoá** · QC PASS 19/19 mục DoD
+ QC-F1/F2/F3, không có vòng fix. Defect đã sửa trong lúc QC: dòng DoD Q15 trỏ vào
`tests/test_portable_sync.py` không tồn tại → đổi sang `tests/test_soul_rules.py` +
`tests/test_step_budget.py` (hai file thật sự khoá `portable/AGENTS.md`).

**Đầu ra:** `skills/tdq-conventions/SKILL.md` · `skills/tdq-conventions/references/context-budget.md`
· `skills/tdq-conventions/references/soul.md` · `portable/AGENTS.md` · `scripts/step_audit.py`
· `scripts/samples/transcript-step-audit.jsonl` · `scripts/token_audit.py` · `scripts/doc_lint.py`
· `tests/test_step_budget.py` · `CHANGELOG.md` + `.claude-plugin/plugin.json` (0.19.0) ·
`docs/kien-truc.md` (bản nháp) · brief/spec/plan/qc của request. Backup: không có sửa ngoài repo.

**Giới hạn:** (1) chưa có bằng chứng tốc độ cải thiện — phải đo lại ở phiên mới, đích là chỉ số
tool call/lượt rời vùng ~1,0. (2) Ảnh base64 trong tool result (93% khối lượng tool result ở
phiên Heineken) đã loại khỏi phạm vi, chưa xử lý. (3) `docs/kien-truc.md` vẫn là bản nháp, user
chưa chốt. (4) Không thêm hook cưỡng chế gộp — hook không phân biệt được call độc lập với call
phụ thuộc, ép cứng sẽ phá bảng Cấm gộp.

**Smoke test (2026-08-15 11:56):** `step_audit.py` chạy trên transcript thật 135 MB (26.562
dòng) → 0,27 s, RSS đỉnh 24 MB, không lỗi; chạy 3 session cùng lúc → 0,25 s. Đọc theo dòng
đúng như thiết kế, không nạp cả file.

**Ước tính mức tối ưu** (đếm trên chính hai transcript thật, kịch bản "luật một lượt được
thi hành đủ"; bỏ được = số lần Read lặp + số bước gộp được của các chuỗi lượt liên tiếp chỉ
gọi tool CHỈ ĐỌC, trần gộp 4–6 lượt, không đụng bước ghi theo bảng Cấm gộp):

| Transcript | Số bước | Kịch bản thận trọng | Kịch bản rộng tay |
|---|---|---|---|
| Heineken (3.397 bước, 5,9 h model) | 3.397 | −351 bước = **10,3%** ≈ 23 phút | −844 bước = **24,8%** ≈ 56 phút |
| Phiên TDQ này (2.626 bước, 5,9 h model) | 2.626 | −353 bước = **13,4%** ≈ 28 phút | −552 bước = **21,0%** ≈ 44 phút |

Con số nên dùng là **~10–15% thời gian mỗi request**, không phải mốc rộng tay. Ba lý do trừ
hao: (1) lượt gộp có tool result to hơn nên chậm hơn một lượt lẻ, tiết kiệm thực < tiết kiệm
bước; (2) một phần Read lặp là ca BẮT BUỘC đọc lại (phiên này bị nén context 2 lần) nên không
được tính là bước thừa; (3) kịch bản rộng tay coi mọi lệnh Bash không có dấu hiệu ghi là gộp
được, thực tế nhiều lệnh phụ thuộc kết quả lệnh trước. Đây là ƯỚC TÍNH trên dữ liệu cũ, không
phải đo sau; số thật chỉ có sau khi chạy một request đầy đủ ở phiên mới.

**Git:** chưa commit — không có commit gỡ chặn nào trong lúc build.
