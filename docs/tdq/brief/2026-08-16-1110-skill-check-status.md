# BRIEF — Skill `check-status`: dò lại request đang dở và tiếp tục không mất dữ liệu

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Ngày: 2026-08-16 11:10 · Lane: full (user chốt sẵn trong yêu cầu)

## Nguyên văn

> tôi muốn tạo ra thêm một skill cho workflow có tên check-status chức năng của skill là sẽ
> sreach xem hiện tại có đang ở request nào không và đang ở phase nào, tiến hành ở phase đó
> tới đâu rồi và đưa ra báo cáo và thông tin và nếu người dùng okay thì sẽ tiếp tục mà không
> bị mất data cũ. được thiết kế để cho use case là ví dụ session lỗi giữa chừng, phải tạo
> session mới, hoặc máy bị lỗi phải qua một máy khác (có config claude y hệt và có bộ workflow
> sẵn), hoặc người dùng chủ đích đưa một agent khác làm một phase trong request và quay lại
> claude code tiếp tục. Yêu cầu tuân thủ soul và thiết kế chuẩn chỉnh, đủ template, chi tiết
> để mọi model từ cao cấp tới thấp cấp đều dễ dàng tuân theo. hãy commit và mở request lane
> full cho yêu cầu cầu

**Cách hiểu đầu tiên:**

- Mục tiêu: một skill mới `check-status` — KHÔI PHỤC ngữ cảnh, không phải báo cáo trạng thái
  thuần. Nó phải trả lời được "request này thật sự đã đi tới đâu trên đĩa", rồi xin phép user
  và tiếp tục đúng chỗ đó mà không ghi đè thứ đã có.
- Phạm vi đoán: skill sống trong plugin `tdq-workflow` (`skills/check-status/`), user gọi được
  bằng `/check-status`; nhiều khả năng cần một script phụ trong `scripts/` để dò đĩa và so
  sánh với `state.json`, vì skill thuần văn bản không tự tính được sha256 hay đếm tick.
- Ba use case user nêu, đều là "state trong file không còn khớp với việc đã làm thật":
  1. session Claude Code chết giữa chừng, mở session mới — mất context hội thoại, còn file.
  2. đổi máy khác (cùng config Claude, có sẵn bộ workflow) — repo có thể được clone/pull, mốc
     thời gian và transcript của máy cũ không còn.
  3. user cố ý giao một phase cho agent khác (Codex/Gemini/…) rồi quay lại Claude Code — file
     có thể đã đổi mà `state.json` chưa được cập nhật, hoặc ngược lại.
- Chỗ chưa rõ (đưa vào interview): quan hệ với skill `tdq-status` đang có (thay thế / bổ sung /
  gộp); mức "tự sửa" cho phép tới đâu khi phát hiện lệch giữa đĩa và state; có cần đọc dấu vết
  của agent ngoài (git log, working log, file mới) hay chỉ đọc tài sản TDQ; hành vi khi có
  nhiều request dở dang; có bắt buộc chạy được ở bản `portable/` (không hook) không.

## Hiểu & kiến thức

### Năng lực dùng được

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | skill khung đang chạy phase analyze |
| tdq-conventions | plugin:tdq-workflow | NỀN | luật chung; skill mới phải trỏ về đây thay vì chép lại |
| tdq-status | plugin:tdq-workflow | DÙNG | ranh giới phải khoá rõ với skill mới (user chốt: hai skill riêng) |
| tdq-spec / tdq-plan / tdq-build | plugin:tdq-workflow | DÙNG | skill mới phải bàn giao đúng về ba skill này khi "tiếp tục" |
| skill-creator | plugin | DÙNG | khuôn tạo skill mới đúng chuẩn Claude Code |
| plugin-dev:skill-development | plugin | DÙNG | luật progressive disclosure, viết description dễ trigger |
| superpowers:writing-skills | plugin | XÉT | trùng phần lớn với hai skill trên; chỉ mở khi cần đối chiếu |
| graphify | plugin | DÙNG | tra node liên quan trước khi tạo hàm mới trong `scripts/` |
| mem0-memory | plugin | DÙNG | chốt xong ghi một fact ngắn về cơ chế khôi phục |
| Đã xét 278 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### Kiến thức từ đọc code (2026-08-16)

- `docs/kien-truc.md` (bản NHÁP) ràng buộc: chỉ `scripts/tdq_state.py` được ghi
  `state.json`; `skills/` chỉ nhắc TÊN LỆNH của `scripts/`; file code mới phải nằm trong
  `scripts/` hoặc `hooks/`; `portable/` phải khớp bước với `skills/`.
- Phần "dò" phần lớn đã có sẵn trong `scripts/tdq_state.py`: `plan_tick_state()` (đếm
  `[x]`/`[~]`/`[ ]` trong plan), `sha256_file()` (bắt spec/plan đổi sau khi duyệt),
  `repo_status_digest()` + `repo_status_paths()` (đọc git status), `find_shadow_states()`
  (dò `state.json` lạc chỗ), `turn_snapshot()`, `render_next()`.
- Skill mới bị 2 test khoá hình dạng: `tests/test_skill_shape.py` (bước đánh số liên tục,
  có `Xong khi:` và `Bước kế tiếp:`, dưới trần dòng) và `doc_lint.SKILL_LINE_LIMITS` —
  phải thêm một dòng trần cho skill mới ở CẢ hai nơi.
- `portable/` hiện có 12 file; thêm bản chép của skill mới là thêm 1 file vào
  `portable/workflow/` và một dòng trong bảng phase của `portable/AGENTS.md`.

### Phạm vi đã chốt

- Mặt CHỌN: chức năng · độ tin cậy · bảo trì · trải nghiệm người dùng (user chọn 1 A B C).
- Mặt LOẠI: bảo mật · hiệu năng runtime · an toàn · đa nền tảng ngoài phạm vi máy user —
  skill chỉ đọc file trong repo của chính user, không có dữ liệu nhạy cảm và không có ngưỡng
  tải; ngoại lệ duy nhất là "đa nền tảng" theo nghĩa Claude Code + agent ngoài, đã nằm trong
  mặt CHỌN qua yêu cầu bản `portable/`.
- Bối cảnh: công cụ dùng hằng ngày, chạy trên nhiều máy cùng config, một người giữ, đã có
  20 bản phát hành và 639 test đang khoá hành vi.
- Mức đầu tư suy ra: đầy đủ — vì hỏng đường khôi phục nghĩa là mất spec/plan/tick của cả
  một request, và user đã chọn cả mặt độ tin cậy lẫn bảo trì.

## Hỏi đáp

### Vòng 1 — scope (2026-08-16 11:10 → 11:18)

1. Request bao quanh mặt nào? → user: **1 A B C** = chức năng + độ tin cậy + bảo trì +
   trải nghiệm (bỏ option D "chỉ cần chạy được").
2. Quan hệ với `tdq-status`? → user: **2 A** = skill RIÊNG, nặng về khôi phục; `tdq-status`
   giữ nguyên vai trò báo nhanh.
3. Chạy ở đâu? → user: **3 A** = cả `skills/` (Claude Code) lẫn bản chép `portable/`.
4. Bổ sung gì không? → user: **4 A** = không, làm tiếp.

### Vòng 2 — chi tiết (2026-08-16 11:20 → 11:26)

1. Tên skill? → user: **1 A** = `tdq-check-status`, cùng họ với 6 skill `tdq-*`.
2. Mức tự sửa khi state lệch đĩa? → user: **2 A** = báo cáo + in đúng lệnh sẽ chạy, user
   gật một lần thì skill tự chạy lệnh vá rồi đi tiếp (một cổng xác nhận duy nhất).
3. Nguồn dò? → user: **3 A** = `docs/tdq/**` + `state.json` + git (log, status) + working
   log hôm nay. KHÔNG đọc transcript session cũ (option C bị loại vì transcript không đi
   theo khi đổi máy).
4. "Tiếp tục" tới đâu? → user: **4 A** = tuỳ phase — phase có cổng duyệt (spec/plan) thì
   trình lại đúng cổng rồi dừng; phase việc máy (implement/qc/report) thì chạy tiếp ngay.
5. Request mồ côi? → user: **5 B** = chỉ lo request đang mở trong state. Không dò, không
   liệt kê, không khôi phục slug mồ côi — cắt khỏi phạm vi.
6. Bổ sung gì không? → user: **6 A** = không, viết spec.

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | việc thuần nội bộ: mọi dữ kiện nằm trong repo này, không có ẩn số bên ngoài |
| Vòng scope | CÓ | đã chạy, dấu hiệu 1 và 2 (yêu cầu gọi tên cả một skill mới, nhiều mặt chưa nói) |
| Interview chi tiết | CÓ | đã chạy 1 vòng 6 câu, hết câu hỏi làm đổi kết quả |
| Spec riêng + plan checkbox | CÓ | khung bất biến của lane full |
| Chia subagent | BỎ | các task nối nhau trên cùng bộ file skill + một script, tách worktree chỉ đẻ xung đột |
| QC độc lập bằng agent | CÓ | user chọn mặt độ tin cậy; luật khôi phục sai là mất dữ liệu, cần một lượt kiểm độc lập bằng `tdq-qc-tester` |
| Review sâu `tdq-reviewer` | BỎ | phạm vi đã khoá bằng 10 câu trả lời của user qua 2 vòng |
| Report | CÓ | khung bất biến |
