# PLAN — Ưu tiên tra ui-ux-pro-max cho các case UI/UX

Ngày: 2026-09-03 · Spec: ../spec/2026-09-03-1949-uiux-pro-max-routing.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — đo bằng `tdq_bench.py mo-phong` trên chính plan này (hệ số agent 1.5): 8 task, 1 đợt, main 16.3 phút / đội 14.3 phút, `Winner: đội` cách 2.0 phút. Khoảng cách mỏng vì `tests/test_uiux_routing.py` là file nóng bốn task cùng ghi nên chỉ 1 task giao ra được, 7 task leader giữ. (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH · Mode thực thi đã chốt: main (user nhắn "1b") · QC 18/18 PASS

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Luật routing UI/UX
- P2 — Vá kiểm kê năng lực
- P3 — Bundle
- P4 — Log & test bắt buộc
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy test của module, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. **Cấm sửa tay file trong ba bundle** và cấm chạm mọi file ngoài repo (`~/.claude/plugins/`,
   thư mục nguồn của plugin ui-ux-pro-max) — spec R1.

## P1 — Luật routing UI/UX

- [x] **T1.1** (e14m) Viết bộ test đọc văn bản luật: có tên `ui-ux-pro-max` trong bảng routing; khối luật nêu đủ ba tầng; có đủ ba tên `frontend-design`/`figma`/`chrome-devtools-mcp`; có câu loại trừ Unity; không chứa từ ra lệnh tuyệt đối trong khối đó — Test: `python3 -m pytest tests/test_uiux_routing.py -q` ĐỎ đúng 5 ca vì luật chưa tồn tại
  - Chạm: `tests/test_uiux_routing.py` → file mới, chưa node nào phụ thuộc

- [x] **T1.2** (e22m) Thêm một dòng UI/UX vào bảng routing và viết khối luật `## UI/UX — three layers` ngay dưới bảng: nêu ba tầng, nói rõ ui-ux-pro-max chỉ phủ tầng giữa, mức ràng buộc "mặc định tra, bỏ qua được nếu nêu lý do một dòng", ba plugin ghép được, câu loại trừ Unity/game — Test: 5 ca của T1.1 chuyển XANH
  - Chạm: `skills/tdq-conventions/references/plugin-routing.md` → mọi skill `tdq-*` đọc file này qua `tdq-conventions`

  - Dùng: `ui-ux-pro-max (7 skill)`
  - Để: đọc mô tả 7 skill của plugin để viết đúng tên và đúng phạm vi từng cái trong
    khối luật. Agent ngoài không có skill system: đọc
    `~/.claude/plugins/.../ui-ux-pro-max/.claude/skills/*/SKILL.md` rồi làm theo.
  - Ra: tên plugin + phạm vi từng skill, nằm trong khối luật của `plugin-routing.md`
  - Kiểm: `pytest -k routing_co_dong_uiux` xanh
  - Không dùng cho: sinh dữ liệu thiết kế cho repo này; không chép catalog vào repo

  - Dùng: `frontend-design`
  - Để: xác định ranh giới với `ui-styling` để câu luật ghép không mâu thuẫn
  - Ra: một mệnh đề trong khối luật nói khi nào hai cái đi cùng nhau
  - Kiểm: `pytest -k ghep_duoc` xanh
  - Không dùng cho: thay thế ui-ux-pro-max ở tầng quyết định thiết kế

  - Dùng: `figma`
  - Để: giữ cho dòng routing mới không mâu thuẫn dòng `figma` đã có (spec R2)
  - Ra: một mệnh đề nói figma dùng khi đã có file thiết kế sẵn (design-to-code)
  - Kiểm: `pytest -k ghep_duoc` xanh
  - Không dùng cho: chọn màu/font/style khi chưa có thiết kế

  - Dùng: `chrome-devtools-mcp` (mcp)
  - Để: trỏ tầng kiểm chứng trên máy thật (a11y, lighthouse) sang đúng chỗ
  - Ra: một mệnh đề nói tầng ba thuộc plugin này, không thuộc ui-ux-pro-max
  - Kiểm: `pytest -k ba_tang` xanh
  - Không dùng cho: quyết định thiết kế; nó chỉ đo cái đã dựng

**Xong P1 khi**: 5 ca test văn bản luật xanh, `doc_lint.py` không kêu trên file luật.

## P2 — Vá kiểm kê năng lực

- [x] **T2.1** (e12m) Thêm ca test cho hàm quét thư mục skill của plugin: dựng plugin giả có skill ở `.claude/skills/` (không có `skills/`) và một plugin giả có `skills/`, khẳng định cả hai đều được liệt kê; thêm ca khẳng định plugin không có skill nào thì không sinh dòng rác — Test: `python3 -m pytest tests/test_uiux_routing.py -q` ĐỎ ở 3 ca mới
  - Chạm: `tests/test_uiux_routing.py` → file nóng, đã tạo ở T1.1

- [x] **T2.2** (e16m) Vá hàm quét trong `skill_inventory.py`: thử `<installPath>/skills` trước, không có thì thử `<installPath>/.claude/skills`; giữ nguyên chữ ký hàm và định dạng đầu ra — Test: 3 ca của T2.1 chuyển XANH
  - Chạm: `scripts/skill_inventory.py` → bước B0 của `tdq-intake` gọi script này

- [x] **T2.3** (e8m) Chạy thật `skill_inventory.py --tat-ca` trên máy này, khẳng định xuất hiện ≥1 dòng nguồn `plugin:ui-ux-pro-max` và tổng số dòng của các nguồn plugin KHÁC không đổi so với trước khi vá — Test: đếm trước/sau, chênh lệch đúng bằng số skill của riêng plugin đó
  - Chạm: `tests/test_uiux_routing.py` → file nóng, đã tạo ở T1.1

**Xong P2 khi**: 3 ca mới xanh và lệnh chạy thật in ra dòng `plugin:ui-ux-pro-max`.

## P3 — Bundle

- [x] **T3.1** (e10m) Dựng lại ba bundle rồi kiểm — Test: `python3 scripts/build_portable.py` chạy sạch, `python3 scripts/tdq_checkportable.py check --root <mỗi bundle>` in CLEAN cho cả ba
  - Chạm: `portable_claude/`, `portable_codex/`, `antigravity_portable/` → sinh ra từ `build_portable.py`, không sửa tay

- [x] **T3.2** (e6m) Thêm ca test khẳng định luật mới CÓ MẶT trong bundle đã dựng (ít nhất bản `portable_claude`), để lần sau ai quên dựng lại thì test bắt được — Test: ca mới xanh sau khi T3.1 xong
  - Chạm: `tests/test_uiux_routing.py` → file nóng, đã tạo ở T1.1

**Xong P3 khi**: ba bundle CLEAN và ca test bundle xanh.

## P4 — Log & test bắt buộc

- [x] **T4.1** (e8m) Chạy toàn bộ suite đúng MỘT lần, đối chiếu mốc đỏ có sẵn, rồi đóng sổ lượt bằng `tdq_finish.py` — Test: `python3 -m pytest -q` không vượt mốc đỏ có sẵn; `tdq_finish.py` in `lint=ok · worklog=ok`

**Xong P4 khi**: suite không xấu đi và sổ công việc đã ghi.

## Cụm song song

Không có cụm nào chạy song song được. `tests/test_uiux_routing.py` bị T1.1, T2.1, T2.3, T3.2
cùng ghi; `plugin-routing.md` bị T1.2 ghi rồi T3.1 đọc lại qua bản dựng. Đây là lý do của
dòng `Mode thực thi` ở đầu file.

## Definition of Done

Chiếu thẳng §6 của spec, 14 dòng, mỗi dòng một lệnh kiểm:

1. Bảng routing có dòng UI/UX nêu đúng tên `ui-ux-pro-max` — `pytest -k routing_co_dong_uiux`.
2. Khối luật nêu đủ ba tầng — `pytest -k ba_tang`.
3. Khối luật nói rõ ui-ux-pro-max chỉ phủ tầng giữa — `pytest -k tang_giua`.
4. Khối luật dùng từ ngữ tra cứu, không có từ ra lệnh tuyệt đối — `pytest -k khong_menh_lenh`.
5. Khối luật nêu mức ràng buộc bỏ qua được kèm lý do một dòng — `pytest -k muc_rang_buoc`.
6. Khối luật nêu đủ ba plugin ghép được — `pytest -k ghep_duoc`.
7. Khối luật nêu câu loại trừ Unity/game — `pytest -k loai_tru_unity`.
8. `skill_inventory.py --tat-ca` in ≥1 dòng `plugin:ui-ux-pro-max` — chạy thật, dán output.
9. Bản vá không đổi số dòng của các nguồn plugin khác — `pytest -k khong_phinh_bang`.
10. Bộ test riêng của request xanh toàn bộ — `python3 -m pytest tests/test_uiux_routing.py -q`.
11. `pytest -q` toàn repo không vượt mốc đỏ có sẵn — chạy một lần ở T4.1.
12. Ba bundle CLEAN — `tdq_checkportable.py check --root <mỗi bundle>`.
13. `doc_lint.py` exit 0 trên brief, spec, plan, QC — `python3 scripts/doc_lint.py <4 file>`.
14. Không file nào ngoài repo bị đụng — `git status` sạch phía ngoài, và hai đường dẫn cấm
    nằm ngoài repo nên không thể xuất hiện trong `git status`.

## Ước tính

7 task, tổng `(e96m)`.
