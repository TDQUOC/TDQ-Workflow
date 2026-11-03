# REPORT — Đo trước ở spec, implement chạy hết plan trong một lượt (`2026-10-03-0732-do-truoc-lam-mot-turn` · lane full · mode subagent · 17/17 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** luật R14 của `doc_lint` — mỗi ngưỡng số ở §6 của spec mới phải có cột `Đo trước`
(số đo hoặc ước lượng có nguồn) và `Dự phòng nếu trượt` · `approve spec` từ chối khi R14 đỏ, lối
thoát `--bo-qua-do "<lý do>"` của user · lệnh `lech add/list/duyet/bac` ghi lệch spec thay cho câu
hỏi giữa chừng; `next` ở qc/report liệt kê lệch chờ duyệt · `pause` chỉ nhận 4 loại bất khả
kháng (`--loai`) · hook `ask_gate.py` (`TDQ:ASK`) nhắc khi agent hỏi bằng popup ở implement/qc —
đường dừng trong ảnh mà cổng Stop không thấy · luật dừng, khuôn spec, QC, report, bảng mã và
quyết định kiến trúc sửa theo.

**Kết quả:** ca 232 MB > 200 MB giờ lộ ra ở spec (R14 chặn duyệt) thay vì giữa implement. R14 trên
spec thật: nhận đúng 10/10 hàng có ngưỡng, 0/10 hàng phép tồn tại, 0 lỗi trên 103 spec cũ. Đo
trước tìm ra một ràng buộc thật trước khi viết plan: `plan-template.md` ở 3.497/3.500 token, nên
cột dự phòng đặt ở spec.

**Kiểm:** trọn bộ `python -m unittest discover tests` → `Ran 2425 · OK (skipped=9)` trên Windows ·
QC **16/17 PASS**, Q17 partial · `code-review` 4 phát hiện: nhận 2 lỗi thật và sửa (R14 chặn oan spec
tiếng Anh; `--json` bẩn), 1 ghi thành lệch, 1 bác · `simplify` 5 chỗ rút gọn, không đổi hành vi ·
`doc_lint skills` exit 0 · `token_budget --kiem` exit 0. QC: `docs/tdq/qc/2026-10-03-0732-do-truoc-lam-mot-turn.md`.

**Đầu ra:** `hooks/scripts/ask_gate.py` · `scripts/doc_lint.py` (R14) · `scripts/tdq_state.py`
(`lech`, `pause --loai`, cổng `approve spec`, khối lệch trong `next`) · `_common.remind(decide=)` ·
6 file luật trong `skills/` · `docs/kien-truc.md` · 5 file test mới · `docs/CHANGELOG-archive-2.md`
(0.38.0–0.37.0 dời ra vì CHANGELOG chạm trần 500 dòng). Không sửa gì ngoài repo.

**Lệch spec:** #1 — **user đã duyệt ("1a", 2026-10-03)**, hai ô của Q1, Q2 đã điền, `doc_lint` trên spec xanh, `approve spec` ghi lại sha mới qua cổng R14 · · Q4 / DoD "doc_lint xanh trên chính spec này" → đo được: R14 bắt Q1, Q2
của spec này (ví dụ `≤ 200 MB` trong backtick, bị bắt sau khi đóng lỗ backtick) · đã áp: giữ spec
nguyên, duyệt thì tôi điền hai ô của Q1, Q2. Lý do: sửa §6 sau khi duyệt làm lệch sha và đòi duyệt
lại giữa implement — đúng kiểu dừng request này bỏ.

**Giới hạn:**
- macOS và Linux chưa chạy trọn bộ test — hai máy không trả lời ping.
- Cổng Stop chưa chặn kết request khi còn lệch chưa duyệt; hiện là luật + dòng `next`.
- Phase analyze của chính request này hỏi bạn bằng popup, trái luật `user-facing-block.md` cấm
  popup ở mọi câu hỏi — lỗi của tôi; hook mới chỉ nhắc ở implement/qc nên không bắt được ca đó.
- Codex không có tool popup nên không có hook nhắc tương đương; luật trong skill vẫn áp.

**Git:** nhánh `feature/do-truoc-lam-mot-turn`, 35 commit trên `main`, chưa merge. Gồm commit làm
việc của team mode (mỗi nhánh con gộp vào nhánh request) và **11 commit sổ sách để mở khoá merge** —
`tdq_team.py` từ chối kiểm/gộp khi bản đồ giao việc cũ hơn plan: `7ebc26b`, `16580ab`, `a978a3c`,
`89a8298`, `9fdc271`, `f92a344`, `db85d6f`, `a5a584b`, `2f1d4e9`, `fddb62c`, `b48f16d`. Bản plugin
bump **0.55.0 → 0.56.0** kèm mục CHANGELOG.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | — | 1 |
| analyze | 9 min | — | 1 |
| spec | 6 min | — | 1 |
| plan | 2h 06min | — | 1 |
| implement | 35 min | — | 1 |
| qc | 1 min | — | 1 |
| report | 5s | — | 1 |
| **Total** | **2h 57min** | **—** | |

Nguyên văn từ `tdq_timing.py show`. `plan` 2h 06min gồm thời gian chờ bạn duyệt plan và chọn
mode, không phải thời gian làm. Cột `Model time` là `—` vì `tdq_timing.py` không đọc được
transcript của phiên Windows này (nợ đã khai từ request trước).
